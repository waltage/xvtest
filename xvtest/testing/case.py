from __future__ import annotations
from typing import Any

from xvtest.adapters.xv6 import Xv6Adapter
from xvtest.adapters.make import MakeAdapter
from xvtest.adapters.anubis import AnubisResult


class Xv6TestCase:
  def __init__(
      self,
      topic: str,
      test_name: str,
      xv6_adapter: Xv6Adapter,
      make_adapter: MakeAdapter,
      hidden: bool = False
  ):

    self.topic: str = topic
    self.test_name: str = test_name
    self.xv6_adapter: Xv6Adapter = xv6_adapter
    self.make_adapter: MakeAdapter = make_adapter
    self.hidden: bool = hidden
    self.result: AnubisResult = AnubisResult(topic, test_name)

  def setup(self):
    self.make_adapter.clean()
    self.make_adapter.build()
    self.xv6_adapter.start_xv6()

  def teardown(self):
    self.xv6_adapter.stop_xv6()
    self.make_adapter.clean()

  def test(self):
    raise NotImplemented

  def update_test_result(self, tr):
    tr.passed = self.result.passed
    tr.message = self.result.message
    tr.output_type = self.result.output_type
    tr.output = self.result.output

  def __call__(self) -> Any:

    try:
      self.setup()
    except Exception as e:
      self.result.fail_with_exception(e)
      self.teardown()
      raise e

    try:
      self.test()
    except Exception as e:
      self.result.fail_with_exception(e)
      self.teardown()
      raise e

    try:
      self.teardown()
    except Exception as e:
      self.result.fail_with_exception(e)
      raise e
