import sys
from typing import Any, Generic, Literal, TypeVar

T = TypeVar("T")


class Variable(Generic[T]):
    def __init__(self, name: str, value: T) -> None:
        self.name = name
        self.type: type[T] = type(value)
        self.value: T = value

    def set(self, new_value: Any):
        if type(new_value) is not self.type:
            print(
                f"Error variable types doesnt match! from {self.type.__name__} to {type(new_value).__name__}"
            )
            sys.exit(1)

        self.value = new_value

    def cast(self, type_converter: Literal[str, int, float, bool, list]):
        old_type = self.type
        try:
            self.type: type[T] = type(type_converter(self.value))
            self.value: T = type_converter(self.value)
        except ValueError:
            print(f"Cannot convert {old_type.__name__} to {type_converter.__name__}")
            sys.exit(1)
