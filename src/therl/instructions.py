import re
import sys

from .types import VARIABLES_TYPE
from .utils import _decode_value
from .variable import Variable


def SET(string: str):
    from .runtime import VARIABLES

    check_slices = string.split(" ")

    if check_slices[1] == "to":
        slices = string.split(" ", maxsplit=2)

        name = slices[0]
        value = slices[2]
        alr_exits = VARIABLES.get(name)

        if alr_exits is not None:
            alr_exits.set(new_value=_decode_value(value))
            return

        VARIABLES[name] = Variable(name=name, value=_decode_value(value))

    elif check_slices[1] == "at":
        slices = string.split(" ", maxsplit=2)

        name = slices[0]
        alr_exits = VARIABLES.get(name)
        if alr_exits is None:
            print(f"Cannot modify unexisisting array named {name}")
            sys.exit(1)

        if alr_exits.type != list and alr_exits.type != str:
            print(
                f"Cannot perform index based modification on {alr_exits.type.__name__}, must list or str"
            )
            sys.exit(1)

        index_and_value = [i.strip() for i in slices[2].split("to")]
        try:
            index = index_and_value[0]
            if VARIABLES.get(index) is not None:
                if VARIABLES.get(index).type != int:
                    print(
                        f"Invalid index type, expected int found {VARIABLES.get(index).type.__name__}"
                    )
                    sys.exit(1)
                index = VARIABLES.get(index).value
            else:
                index = int(index)
        except ValueError:
            print("Invalid index type, expected int found str")
            sys.exit(1)
        value = index_and_value[1]
        try:
            VARIABLES[name].value[index] = (
                _decode_value(value) if alr_exits.type == list else str(value)
            )
        except IndexError:
            print("Index out of range!")
            sys.exit(1)

    else:
        print("invalid syntax expected 'to' in variable assignment")
        sys.exit(1)


def SAY(string: str):
    from .runtime import VARIABLES

    alr_exits = VARIABLES.get(string.strip())

    if "at" in string:
        var_and_index = [s.strip() for s in string.split("at")]
        name = var_and_index[0]

        if VARIABLES.get(name) is None:
            print(f"Variable with name {name} doesnt exist")
            sys.exit(1)

        try:
            index = var_and_index[1]
            if VARIABLES.get(index) is not None:
                if VARIABLES.get(index).type != int:
                    print(
                        f"Invalid index type, expected int found {VARIABLES.get(index).type.__name__}"
                    )
                    sys.exit(1)
                index = VARIABLES.get(index).value
            else:
                index = int(index)
        except ValueError:
            print("Invalid index type, expected int found str")
            sys.exit(1)

        try:
            print(VARIABLES[name].value[index])
            return
        except IndexError:
            print("Index out of range")
            sys.exit(1)

    if alr_exits is not None:
        print(alr_exits.value)
        return

    print(_decode_value(string))


def CAST(string: str):
    from .runtime import VARIABLES

    slices = [s.strip() for s in string.split("to") if s]
    name = slices[0]
    new_type = slices[1]
    alr_exits = VARIABLES.get(name)

    if alr_exits is None:
        print(f"Variable with name {name} doesnt exist")
        sys.exit(1)

    if new_type == "int":
        alr_exits.cast(int(alr_exits.value))

    elif new_type == "float":
        alr_exits.cast(float(alr_exits.value))

    elif new_type == "str":
        alr_exits.cast(str(alr_exits.value))

    elif new_type == "array":
        alr_exits.cast(list(alr_exits.value))

    else:
        print(f"Invalid type {new_type}")
        sys.exit(1)


def ADD(string: str):
    from .runtime import VARIABLES

    slices = [s.strip() for s in string.split("to") if s]
    name = slices[1]
    new_value = _decode_value(slices[0])
    alr_exits = VARIABLES.get(name)

    if alr_exits is None:
        print(f"Variable with name {name} doesnt exist")
        sys.exit(1)

    if alr_exits.type != list:
        print(f"Variable must be an array not a {alr_exits.type.__name__}")
        sys.exit(1)

    alr_exits.value.append(new_value)


def RUN(string: str):
    from .functions import Function
    from .runtime import VARIABLES

    slices = [_.strip() for _ in string.split(" ") if _]

    func_name = slices[0]

    if VARIABLES.get(func_name) is None:
        print(f"Function named {func_name} doesnt exist!")
        sys.exit(1)

    if VARIABLES.get(func_name).type != Function:
        print(
            f"Cant run variable of type {VARIABLES.get(func_name).type.__name__}, must be a function!"
        )
        sys.exit(1)

    if len(slices) == 1:
        VARIABLES[func_name].value.run()
        return

    if slices[1] == "with":
        params: VARIABLES_TYPE = {}
        params_slices = [_.strip() for _ in " ".join(slices[2:]).split("and")]

        for param in params_slices:
            s = [_.strip() for _ in re.split(re.escape(" "), param) if _]
            if s[1] != "as":
                print(f"Expected as in parameter assignment, found {s[1]}")
                sys.exit()
            name = s[0].strip().replace("<", "").replace(">", "")

            if name not in VARIABLES.get(func_name).value.params:
                print(f"Unknown parameter {name}")
                sys.exit(1)

            value = s[2].strip()

            if VARIABLES.get(value) is not None:
                params[name] = VARIABLES.get(value)
            else:
                params[name] = Variable(name=name, value=_decode_value(value))

        VARIABLES[func_name].value.run(params=params)
