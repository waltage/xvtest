from __future__ import annotations

_MaybeExc = [Exception, None]


class AutoGradeError(BaseException):
  def __init__(
      self,
      location: str,
      message: str,
      exc: _MaybeExc = None):
    self.location = location
    self.message = message
    self.exc = exc

  def __str__(self):
    if self.exc:
      return "{:s}::{:s}|exception={:s}".format(
        self.location,
        self.message,
        self.exc
      )
    else:
      return "{:s}::{:s}".format(
        self.location,
        self.message,
      )


class BuildError(AutoGradeError):
  def __init__(self, location: str, message: str, exc: _MaybeExc = None):
    super(BuildError, self).__init__(location, message, exc)


class BuildMakeError(BuildError):
  def __init__(self, message: str, exc: _MaybeExc = None):
    super(BuildMakeError, self).__init__("make", message, exc)


class BuildCleanError(BuildError):
  def __init__(self, message: str, exc: _MaybeExc = None):
    super(BuildCleanError, self).__init__("make clean", message, exc)


class Xv6AdapterError(AutoGradeError):
  def __init__(self, location: str, message: str, exc: _MaybeExc = None):
    super(Xv6AdapterError, self).__init__(location, message, exc)


class Xv6AdapterBootError(Xv6AdapterError):
  def __init__(self, message: str, exc: _MaybeExc = None):
    super(Xv6AdapterBootError, self).__init__("boot", message, exc)


class Xv6AdapterIOError(Xv6AdapterError):
  def __init__(self, message: str, exc: _MaybeExc = None):
    super(Xv6AdapterIOError, self).__init__("io", message, exc)


class PipelineError(AutoGradeError):
  def __init__(self, location: str, message: str, exc: _MaybeExc = None):
    super(PipelineError, self).__init__(location, message, exc)


class PipelineMetadataError(PipelineError):
  def __init__(self, message: str, exc: _MaybeExc = None):
    super(PipelineMetadataError, self).__init__("metadata", message, exc)


class Xv6CommandError(AutoGradeError):
  def __init__(self, location: str, message: str, exc: _MaybeExc = None):
    super(Xv6CommandError, self).__init__(location, message, exc)


class Xv6CommandConsoleMirrorError(Xv6CommandError):
  def __init__(self, message: str):
    super(Xv6CommandConsoleMirrorError, self).__init__("console read-back", message)


class Xv6CommandResponseError(Xv6CommandError):
  def __init__(self, location: str, message: str):
    super(Xv6CommandResponseError, self).__init__(location, message)


class TestCaseError(AutoGradeError):
  def __init__(self, message: str):
    super(TestCaseError, self).__init__("test case", message)


class TestCaseExecErrors(TestCaseError):
  def __init__(self, last_line: str):
    super(TestCaseExecErrors, self).__init__(
      "could not execute (errors): last line={}".format(last_line))


class TestCaseIncorrect(TestCaseError):
  def __init__(self):
    super(TestCaseIncorrect, self).__init__("incorrect result")