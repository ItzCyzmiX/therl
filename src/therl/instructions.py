import re
import sys
from typing import Any

from therl.error import RunningNonFunctionObject, UnknownFunction
from therl.types import VARIABLES_TYPE
from therl.utils import _decode_value
from therl.variable import Variable


def SET(string: str, line: int = 1):
    import therl.runtime

    check_slices = string.split(" ")

    if check_slices[1] == "to":
        slices = string.split(" ", maxsplit=2)

        name = slices[0]

        value = _decode_value(slices[2], line=line)
        alr_exits = therl.runtime.VARIABLES.get(name)

        if alr_exits is not None:
            alr_exits.set(new_value=value)
            return

        therl.runtime.VARIABLES[name] = Variable(name=name, value=value)

    elif check_slices[1] == "at":
        slices = string.split(" ", maxsplit=2)

        name = slices[0]
        alr_exits = therl.runtime.VARIABLES.get(name)
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
            if therl.runtime.VARIABLES.get(index) is not None:
                if therl.runtime.VARIABLES.get(index).type != int:
                    print(
                        f"Invalid index type, expected int found {therl.runtime.VARIABLES.get(index).type.__name__}"
                    )
                    sys.exit(1)
                index = therl.runtime.VARIABLES.get(index).value
            else:
                index = int(index)

        except ValueError:
            print("Invalid index type, expected int found str")
            sys.exit(1)
        value = index_and_value[1]
        try:
            therl.runtime.VARIABLES[name].value[index] = (
                _decode_value(value, line=line)
                if alr_exits.type == list
                else str(_decode_value(value, line=line))
            )
        except IndexError:
            print("Index out of range!")
            sys.exit(1)

    else:
        print("invalid syntax expected 'to' or 'at' in variable assignment")
        sys.exit(1)


def SAY(string: str, line: int = 1):
    from therl.runtime import VARIABLES

    alr_exits = VARIABLES.get(string.strip())

    if alr_exits is not None:
        print(alr_exits.value)
        return

    print(_decode_value(string, line=line))


def CAST(string: str, line: int = 1):
    import therl.runtime

    slices = [s.strip() for s in string.split("to") if s]
    name = slices[0]
    new_type = slices[1]
    alr_exits = therl.runtime.VARIABLES.get(name)

    if alr_exits is None:
        print(f"Variable with name {name} doesnt exist")
        sys.exit(1)

    match new_type:
        case "int":
            alr_exits.cast(int)

        case "float":
            alr_exits.cast(float)

        case "string":
            alr_exits.cast(str)

        case "array":
            alr_exits.cast(list)

        case _:
            print(f"Invalid type {new_type}")
            sys.exit(1)


def ADD(string: str, line: int = 1):
    import therl.runtime

    slices = [s.strip() for s in string.split("to") if s]
    name = slices[1]
    new_value = _decode_value(slices[0])
    alr_exits = therl.runtime.VARIABLES.get(name)

    if alr_exits is None:
        print(f"Variable with name {name} doesnt exist")
        sys.exit(1)

    if alr_exits.type != list:
        print(f"Variable must be an array not a {alr_exits.type.__name__}")
        sys.exit(1)

    alr_exits.value.append(new_value)


def RUN(string: str, line: int = 1) -> Any:
    import therl.runtime
    from therl.functions import Function

    slices = [_.strip() for _ in string.split(" ") if _]

    func_name = slices[0]

    if therl.runtime.VARIABLES.get(func_name) is None:
        raise UnknownFunction(var_name=func_name, line=line)

    if not isinstance(therl.runtime.VARIABLES.get(func_name).value, Function):
        raise RunningNonFunctionObject(
            var_name=func_name,
            type_=therl.runtime.VARIABLES.get(func_name).type.__name__,
            line=line,
        )

    if len(slices) == 1:
        return therl.runtime.VARIABLES[func_name].value.run()

    if slices[1] == "with":
        params: VARIABLES_TYPE = {}
        params_slices = [_.strip() for _ in " ".join(slices[2:]).split("and")]

        for param in params_slices:
            s = [_.strip() for _ in re.split(re.escape(" "), param) if _]
            if s[1] != "as":
                print(f"Expected as in parameter assignment, found {s[1]}")
                sys.exit(1)

            name = s[0].strip().replace("<", "").replace(">", "")

            if name not in therl.runtime.VARIABLES.get(func_name).value.params:
                print(f"Unknown parameter {name}")
                sys.exit(1)

            value = s[2].strip()

            if therl.runtime.VARIABLES.get(value) is not None:
                params[name] = therl.runtime.VARIABLES.get(value)
            else:
                params[name] = Variable(name=name, value=_decode_value(value))

        return therl.runtime.VARIABLES[func_name].value.run(params=params)


def RETURN(string: str, line: int = 1) -> Any:
    import therl.runtime
    from therl.functions import Function

    if "with" in string.strip().split(" "):
        slices = string.strip().split("with")
        func_name = slices[0]
        alr_exists = therl.runtime.VARIABLES.get(func_name.strip())

        if alr_exists is None:
            raise UnknownFunction(var_name=func_name, line=line)

        if alr_exists.type != Function:
            print(f"Variable nammed {func_name} isnt a function!")
            sys.exit(1)

        return RUN(string.strip())

    alr_exists = therl.runtime.VARIABLES.get(string.strip())

    if alr_exists is None:
        return _decode_value(string.strip())

    if alr_exists.type == Function:
        return alr_exists.value.run()
    else:
        return alr_exists.value
