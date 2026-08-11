class InvalidSyntax(Exception):
    def __init__(self, wrong_syntax: str, line: int):
        super().__init__(f"Invalid syntax at line {line}: \n {wrong_syntax} ")


class InvalidIndex(Exception):
    def __init__(self, wrong_index, line: int) -> None:
        super().__init__()


class IndexOutOfRange(Exception):
    def __init__(self, index, max_index, line) -> None:
        super().__init__(
            f"Index out of range at line {line}\nGot {index} while array has {max_index} elements"
        )


class InvalidType(Exception):
    def __init__(self, supposed_type: str, wrong_type: str, line: int) -> None:
        super().__init__(
            f"Invalid type at line {line}\nExpected {supposed_type} got {wrong_type}"
        )


class UnknownVariable(Exception):
    def __init__(self, var_name: str, line: int):
        super().__init__(
            f"Invalid Variable Name at line {line}\nVariable nammed {var_name} doesnt exist"
        )


class RunningNonFunctionObject(Exception):
    def __init__(self, var_name: str, type_: str, line: int):
        super().__init__(
            f"Invalid RUN Instruction at line {line}\nCant run variable of {var_name} type {type_}, must be a function!"
        )


class UnknownFunction(Exception):
    def __init__(self, var_name: str, line: int):
        super().__init__(
            f"Invalid Function Name at line {line}\nFunction nammed {var_name} doesnt exist"
        )


class UnknownAttribute(Exception):
    def __init__(self, object_name: str, attr_name: str, line: int):
        super().__init__(
            f"Invalid Attribute at line {line}\nAttribute nammed {attr_name} doesnt exist in object {object_name}"
        )
