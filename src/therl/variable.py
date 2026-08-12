import sys
from typing import Any, Generic, Literal, TypeVar

from therl.error import InvalidType

T = TypeVar("T")


class Variable(Generic[T]):
    def __init__(self, name: str, value: T) -> None:
        self.name = name
        self.type: type[T] = type(value)
        self.value: T = value

    def set(self, new_value: Any, line: int):
        if not isinstance(new_value, self.type):
            raise InvalidType(
                wrong_type=type(new_value).__name__,
                supposed_type=self.type.__name__,
                line=line,
            )

        self.value = new_value
