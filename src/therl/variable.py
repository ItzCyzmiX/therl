from typing import Any, Generic, TypeVar

from therl.error import InvalidKeyword, InvalidType

T = TypeVar("T")


class Variable(Generic[T]):
    def __init__(self, name: str, value: T, line: int = 0) -> None:
        if name == "true" or name == "false":
            raise InvalidKeyword(
                wrong_keyword=name, supposed_keyword="variable", line=line
            )
        self.name = name
        self.type: type[T] = type(value)
        self.value: T = value

    def set(self, new_value: Any, line: int):

        if self.name == "true" or self.name == "false":
            raise InvalidKeyword(
                wrong_keyword=self.name, supposed_keyword="variable", line=line
            )

        if not isinstance(new_value, self.type):
            raise InvalidType(
                wrong_type=type(new_value).__name__,
                supposed_type=self.type.__name__,
                line=line,
            )

        self.value = new_value
