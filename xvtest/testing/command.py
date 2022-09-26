from __future__ import annotations

import re
import time

from xvtest.adapters.xv6 import Xv6Adapter
from xvtest.exceptions import Xv6CommandConsoleMirrorError
from xvtest.exceptions import Xv6CommandResponseError


class Xv6BaseCommand:
  """Base class for xv6 commands."""

  def __init__(self, send: bytes, recv_size: int = -1, timeout: float = 0.5):
    self.timeout = timeout
    self.send_bytes: bytearray = bytearray(send)
    self.response = dict(
      expected_size=recv_size,
      actual_size=0,
      bytes=bytearray(),
      err=bytearray()
    )

  def _send_command(self, adapter: Xv6Adapter):
    if self.send_bytes[-1:] != b'\n':
      self.send_bytes.extend(b'\n')
    adapter.send_stdin(self.send_bytes)
    result = adapter.read_stdout(len(self.send_bytes))
    if result != self.send_bytes:
      raise Xv6CommandConsoleMirrorError("received: {}".format(repr(result)))

  def _fill_response(self, adapter: Xv6Adapter):
    if self.response["expected_size"] == -1:
      # expect no output... verify shell prompt is present
      ahead = adapter.peek_stdout(2)
      if ahead != b'$ ':
        self.response["err"] = adapter.read_stdout(0)
        adapter.stop_xv6()
        raise Xv6CommandResponseError(
          "shell prompt expected",
          "received {}".format(repr(self.response["err"])))
      else:
        # got a shell prompt... skip it
        adapter.seek_stdout(2)
        return

    if self.response["expected_size"] > -1:
      self.response["bytes"] = adapter.read_stdout(
        self.response["expected_size"])
      self.response["actual_size"] = len(self.response["bytes"])

  def _check_response(self):
    panic_messages = (
      "unexpected trap",
      "panic",
      "--kill proc",
    )
    needles = "({})".format("|".join(panic_messages))

    panics = re.search(
      bytes(needles, "utf-8"),
      self.response["bytes"])
    if panics:
      raise Xv6CommandResponseError("unrecoverable error",
                                    "got panic/trap: {}".format(panics.groups()))

  def execute_on(self, adapter: Xv6Adapter):
    self._send_command(adapter)
    time.sleep(self.timeout)
    # this throws....
    self._fill_response(adapter)
    # this throws....
    self._check_response()

  def as_lines(self):
    if self.response["actual_size"] == 0:
      return []
    else:
      return self.response["bytes"].splitlines(False)


class Xv6VoidCommand(Xv6BaseCommand):
  """Execute a command with no expected response."""

  def __init__(self, cmd: str, timeout: float = 0.5):
    super(Xv6VoidCommand, self).__init__(
      bytearray(cmd, "utf-8"),
      -1,
      timeout
    )


class Xv6StaticCommand(Xv6BaseCommand):
  """Execute a command with a fixed-sized expected response."""

  def __init__(self, cmd: str, n: int, timeout: float = 0.5):
    super(Xv6StaticCommand, self).__init__(
      bytearray(cmd, "utf-8"),
      n,
      timeout
    )


class Xv6VariableCommand(Xv6BaseCommand):
  """Execute a command with a variable-sized expected resuponse"""

  def __init__(self, cmd: str, timeout: float = 0.5):
    super(Xv6VariableCommand, self).__init__(
      bytearray(cmd, "utf-8"),
      0,
      timeout
    )


"""
TODO(dwalt): add trap codes
// Processor-defined:
#define T_DIVIDE         0      // divide error
#define T_DEBUG          1      // debug exception
#define T_NMI            2      // non-maskable interrupt
#define T_BRKPT          3      // breakpoint
#define T_OFLOW          4      // overflow
#define T_BOUND          5      // bounds check
#define T_ILLOP          6      // illegal opcode
#define T_DEVICE         7      // device not available
#define T_DBLFLT         8      // double fault
// #define T_COPROC      9      // reserved (not used since 486)
#define T_TSS           10      // invalid task switch segment
#define T_SEGNP         11      // segment not present
#define T_STACK         12      // stack exception
#define T_GPFLT         13      // general protection fault
#define T_PGFLT         14      // page fault
// #define T_RES        15      // reserved
#define T_FPERR         16      // floating point error
#define T_ALIGN         17      // aligment check
#define T_MCHK          18      // machine check
#define T_SIMDERR       19      // SIMD floating point error

// These are arbitrarily chosen, but with care not to overlap
// processor defined exceptions or interrupt vectors.
#define T_SYSCALL       64      // system call
#define T_DEFAULT      500      // catchall

#define T_IRQ0          32      // IRQ 0 corresponds to int T_IRQ

#define IRQ_TIMER        0
#define IRQ_KBD          1
#define IRQ_COM1         4
#define IRQ_IDE         14
#define IRQ_ERROR       19
#define IRQ_SPURIOUS    31

"""
