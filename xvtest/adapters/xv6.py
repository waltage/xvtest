from __future__ import annotations

import io
import os
import logging
import subprocess
import select
import threading
import time

from typing import Callable

from xvtest.exceptions import Xv6AdapterBootError
from xvtest.exceptions import Xv6AdapterIOError

ADAPTER_OUT_PATH = "./xv6adapter.stdout"


class Xv6AdapterConfig:
  """Options for configuring xv6 adapters."""
  def __init__(self, log_name: str = "default"):
    self.logger = logging.getLogger("Xv6Adapter.{}".format(log_name))
    self.xv6_buffer = 1024
    self.xv6_cwd = os.getcwd()


def _xv6_safecall(fn) -> Callable:
  def _wrap(self: Xv6Adapter, *args, **kwargs):
    try:
      return fn(self, *args, **kwargs)
    except Exception as e:
      self.conf.logger.error(
        "error with call %s: '%s'", fn.__name__, e)
      self.stop_xv6()
      raise Xv6AdapterIOError("error in {}".format(fn.__name__), e)
  return _wrap


class Xv6Adapter:
  """Primary interface for interacting with an xv6 session."""
  def __init__(self, config: Xv6AdapterConfig):
    self.conf = config
    self.active = False
    self.xv6_session = None
    self._internal_buffer_rd = None
    self._internal_buffer_wr = None

  @_xv6_safecall
  def send_stdin(self, buffer: bytes) -> None:
    self.conf.logger.debug("xv6 send_stdin: ->{%s}", buffer)
    os.write(self.xv6_session.stdin.fileno(), buffer)
    time.sleep(0.5)

  @_xv6_safecall
  def peek_stdout(self, n: int = 1) -> bytearray:
    self.conf.logger.debug("xv6 peek(%d)", n)
    curr = os.lseek(self._internal_buffer_rd, 0, os.SEEK_CUR)
    result = os.pread(self._internal_buffer_rd, n, curr)
    return bytearray(result)

  @_xv6_safecall
  def seek_stdout(self, n: int = 1):
    os.lseek(self._internal_buffer_rd, n, os.SEEK_CUR)

  @_xv6_safecall
  def read_stdout(self, n: int = 0) -> bytearray:
    self.conf.logger.debug("xv6 read_stdout: request(%d) bytes", n)
    if n == 0:
      result = bytearray(self.conf.xv6_buffer)
    else:
      result = bytearray(n)
    size = os.readv(self._internal_buffer_rd, [result, ])
    result = result[:size]
    return bytearray(result)

  def start_xv6(self):
    os.chdir(self.conf.xv6_cwd)
    cmd = [
      "qemu-system-i386",
      "-drive", "file=xv6.img,media=disk,index=0,format=raw",
      "-drive", "file=fs.img,index=1,media=disk,format=raw",
      "-smp", "2",
      "-m", "512",
      "-display", "none",
      "-nographic",
    ]
    try:
      create_flags = os.O_CREAT | os.O_RDWR | os.O_NONBLOCK
      self._internal_buffer_rd = os.open(ADAPTER_OUT_PATH, create_flags)

      self._internal_buffer_wr = open(ADAPTER_OUT_PATH, "wb")
    except Exception as e:
      raise Xv6AdapterIOError("could not initialize redirect pipes", e)

    self.xv6_session = subprocess.Popen(
      cmd,
      close_fds=True,
      stdout=self._internal_buffer_wr,
      stdin=subprocess.PIPE,
      cwd=self.conf.xv6_cwd)

    self.conf.logger.debug("xv6 session: boot initialized")

    self.active = True
    time.sleep(4)

    bootscreen = self.read_stdout()
    tail = bootscreen[-20:]
    self.conf.logger.debug("xv6 session: boot tail {%s}", bytes(tail))

    if tail != b'init: starting sh\n$ ':
      self.conf.logger.error("xv6 session: bad boot tail", )
      self.stop_xv6()
      raise Xv6AdapterBootError("bad boot tail {}".format(repr(tail)))

    self.conf.logger.debug("xv6 session: successful boot")

  def stop_xv6(self):
    self.conf.logger.debug("xv6 session: terminating qemu")

    if self._internal_buffer_rd:
      os.close(self._internal_buffer_rd)
      self._internal_buffer_rd = None

    if self._internal_buffer_wr:
      self._internal_buffer_wr.close()
      self._internal_buffer_wr = None

    if os.path.exists(ADAPTER_OUT_PATH):
      os.remove(ADAPTER_OUT_PATH)

    if self.active:
      if self.xv6_session:
        self.xv6_session.kill()
        self.conf.logger.debug("xv6 session: terminated.")
      self.active = False