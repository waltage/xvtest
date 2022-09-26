from __future__ import annotations
from typing import Union

_maybeStr = Union[str, None]

class AnubisResult(object):
    def __init__(self, topic: str, name: str):
        self.topic: str = topic
        self.name: str = name
        self.passed: bool = False
        self.hint: _maybeStr  = None
        self.expected: _maybeStr = None
        self.actual: _maybeStr = None

    def __repr__(self):
        return "<AnubisResult  message='{}'\tpassed={} output='{}'\n>".format(
            self.message[:15],
            self.passed,
            self.output[:15],
        )

    def succeed(self):
        self.passed = True

    def fail_with_diff(self, expected: str, actual: str):
        self.expected = expected
        self.actual = actual

    def fail_with_exception(self, error: Exception):
        self.passed = False
        self.hint = str(error)

    @property
    def output_type(self):
        return "text"
    
    @property
    def message(self):
        return "{}::{}".format(self.topic, self.name)

    @property
    def output(self):
        if self.passed:
            return "Passed."

        msg = []
        if self.hint:
            msg.append(self.hint)
        if self.expected:
            msg.append("Expected:")
            msg.append(self.expected)
        if self.actual:
            msg.append("Actual:")
            msg.append(self.actual)

        return "\n".join(msg)