import logging
import subprocess
import os

from xvtest.exceptions import BuildMakeError
from xvtest.exceptions import BuildCleanError


class MakeAdapterConfig:
  def __init__(self, log_name: str = "default"):
    self.logger = logging.getLogger("MakeAdapter.{}".format(log_name))
    self.make_cwd = os.getcwd()
    self.prod = False


class MakeAdapter:
  def __init__(self, build_conf: MakeAdapterConfig):
    self.conf = build_conf

  def build(self):
    self.conf.logger.debug("make: building")

    if self.conf.prod:
      cmd = [
        "env", "-i", "PATH={}".format(os.environ["PATH"]),
        "su", "student", "-c",
        "make"
      ]
    else:
      cmd = ["make",]

    make_session = subprocess.Popen(
      cmd, 
      stdout=subprocess.PIPE, 
      stderr=subprocess.PIPE, 
      cwd=self.conf.make_cwd)
    make_session.wait(4)
    if make_session.returncode != 0:
      self.conf.logger.error("make: build -- non-zero exit code")
      raise BuildMakeError("non-zero exit code")
    self.conf.logger.debug("make: build complete.")

  def clean(self):
    self.conf.logger.debug("make: cleaning")

    if self.conf.prod:
      cmd = [
        "env", "-i", "PATH={}".format(os.environ["PATH"]),
        "su", "student", "-c",
        "make", "clean",
      ]
    else:
      cmd = ["make", "clean", ]

    make_session = subprocess.Popen(
      cmd, 
      stdout=subprocess.PIPE, 
      stderr=subprocess.PIPE,
      cwd=self.conf.make_cwd)
    make_session.wait(3)
    if make_session.returncode != 0:
      self.conf.logger.error("make: clean -- non-zero exit code")
      raise BuildCleanError("non-zero exit code")
    self.conf.logger.debug("make: clean complete.")