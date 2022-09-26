from __future__ import annotations

from typing import List

from xvtest.adapters.xv6 import Xv6Adapter
from xvtest.testing.command import Xv6VariableCommand
from xvtest.testing.fs import FileStat


class BuiltinLS:
  def __init__(self, cwd: str, path: str):
    if cwd[-1] == "/":
      cwd = cwd[:-1]
    self.cwd = cwd
    self.path = path
    self.result: List[FileStat] = []

  def execute_on(self, adapter: Xv6Adapter):
    cmd = Xv6VariableCommand("/ls {}/{}".format(self.cwd, self.path))
    cmd.execute_on(adapter)
    for entry in cmd.as_lines()[:-1]:
      self.result.append(
        FileStat(self.cwd, entry)
      )
