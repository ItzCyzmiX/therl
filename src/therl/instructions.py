import re
import sys
from typing import Any

from therl.error import (
    IndexOutOfRange,
    InvalidSyntax,
    InvalidType,
    RunningNonFunctionObject,
    UnknownFunction,
    UnknownParameter,
    UnknownVariable,
)
from therl.types import VARIABLES_TYPE
from therl.utils import _decode_value
from therl.variable import Variable


def SET(string: str, line: int = 1):
    from therl.api import THERL

    check_slices = string.split(" ")

    if check_slices[1] == "to":
        slices = string.split(" ", maxsplit=2)

        name = slices[0]

        value = _decode_value(slices[2], line=line)
        alr_exits = THERL.runtime.get(name)

        if alr_exits is not None:
            alr_exits.set(new_value=value)
            return

        THERL.runtime.new(name, value)

    elif check_slices[1] == "at":
        slices = string.split(" ", maxsplit=2)

        name = slices[0].strip()
        alr_exits = THERL.runtime.get(name)

        if alr_exits is None:
            raise UnknownVariable(var_name=name, line=line)

        if not isinstance(alr_exits.value, (list, str)):
            raise InvalidType(
                wrong_type=alr_exits.type.__name__,
                supposed_type="array or str",
                line=line,
            )

        index_and_value = [i.strip() for i in slices[2].split("to")]

        index = _decode_value(index_and_value[0], line=line)

        if not isinstance(index, int):

            raise InvalidType(
                wrong_type=type(index).__name__,
                supposed_type="array or str",
                line=line,
            )

        value = index_and_value[1]

        try:
            THERL.runtime.change_at_index(
                name,
                index,
                (
                    _decode_value(value, line=line)
                    if alr_exits.type == list
                    else str(_decode_value(value, line=line))
                ),
            )
        except IndexError:
            raise IndexOutOfRange(
                index=index, max_index=len(alr_exits.value), line=line
            )
    else:
        raise InvalidSyntax(
            wrong_syntax=f"Expected 'to' or 'at' in variable assignment, found {check_slices[1]}"
        )


def SAY(string: str, line: int = 1):
    from therl.api import THERL

    alr_exits = THERL.runtime.get(string.strip())

    if alr_exits is not None:
        print(alr_exits.value)
        return

    print(_decode_value(string, line=line))


def CAST(string: str, line: int = 1):
    from therl.api import THERL

    slices = [s.strip() for s in string.split("to") if s]
    name = slices[0].strip()
    new_type = slices[1].strip()
    alr_exits = THERL.runtime.get(name)

    if alr_exits is None:
        raise UnknownVariable(var_name=name, line=line)

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
    from therl.api import THERL

    slices = [s.strip() for s in string.split("to") if s]
    name = slices[1]
    new_value = _decode_value(slices[0], line=line)
    alr_exits = THERL.runtime.get(name)

    if alr_exits is None:
        raise UnknownVariable(var_name=name, line=line)

    if not isinstance(alr_exits.value, (list, str)):
        raise InvalidType(
            supposed_type="array or str", wrong_type=alr_exits.type.__name__, line=line
        )

    if isinstance(alr_exits.value, list):
        alr_exits.value.append(new_value)
    else:
        alr_exits.value += str(new_value)


def RUN(string: str, line: int = 1) -> Any:
    from therl.api import THERL
    from therl.functions import Function

    slices = [_.strip() for _ in string.split(" ") if _]

    func_name = slices[0]

    if THERL.runtime.get(func_name) is None:
        raise UnknownFunction(var_name=func_name, line=line)

    if not isinstance(THERL.runtime.get(func_name).value, Function):
        raise RunningNonFunctionObject(
            var_name=func_name,
            type_=THERL.runtime.get(func_name).type.__name__,
            line=line,
        )

    if len(slices) == 1:
        return THERL.runtime.get(func_name).value.run()

    if slices[1] == "with":
        params: VARIABLES_TYPE = {}
        params_slices = [_.strip() for _ in " ".join(slices[2:]).split("and")]

        for param in params_slices:
            s = [_.strip() for _ in re.split(re.escape(" "), param) if _]
            if s[1] != "as":
                raise InvalidSyntax(
                    wrong_syntax=f"Expected as in parameter assignment, found {s[1]}"
                )

            name = s[0].strip().replace("<", "").replace(">", "")

            if name not in THERL.runtime.get(func_name).value.params:
                raise UnknownParameter(
                    func_name=func_name,
                    wrong_param=name,
                    params=THERL.runtime.get(func_name).value.params,
                    line=line,
                )

            value = s[2].strip()

            if THERL.runtime.get(value) is not None:
                params[name] = THERL.runtime.get(value)
            else:
                params[name] = Variable(name=name, value=_decode_value(value))

        return THERL.runtime.get(func_name).value.run(params=params)


def RETURN(string: str, line: int = 1) -> Any:
    from therl.api import THERL
    from therl.functions import Function

    if "with" in string.strip().split(" "):
        slices = string.strip().split("with")
        func_name = slices[0]
        alr_exists = THERL.runtime.get(func_name.strip())

        if alr_exists is None:
            raise UnknownFunction(var_name=func_name, line=line)

        if not isinstance(alr_exists.value, Function):
            raise RunningNonFunctionObject(
                var_name=func_name, type_=alr_exists.type.__name__, line=line
            )

        return RUN(string.strip())

    alr_exists = THERL.runtime.get(string.strip())

    if alr_exists is None:
        return _decode_value(string.strip())

    if isinstance(alr_exists.value, Function):
        return alr_exists.value.run()
    else:
        return alr_exists.value
