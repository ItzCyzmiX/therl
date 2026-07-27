import sys
from typing import Any, Generic, TypeVar

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

    def cast(self, new_value: T):
        self.type: type[T] = type(new_value)
        self.value: T = new_value
