import re
from typing import Any

from therl.error import (
    IndexOutOfRange,
    InvalidKeyword,
    InvalidType,
    InvalidVariableCasting,
    UnknownVariable,
    UnknownAttribute,
)
from therl.lib import simpleval


def _decode_value(value: str, line: int = 1) -> Any:

    # check array
    if value[0] == "[" and value[-1] == "]":
        return _decode_array(value, line=line)

    ssplit = [
        s.strip()
        for s in re.split(
            f"({'|'.join(map(re.escape, ['as', 'to', "from", "run", "at"]))})", value
        )
    ]

    # check running a function (getting its return value)
    if ssplit[0].strip() == "run":
        return _decode_run_instruction(value=value, line=line)

    if len(ssplit) > 2:
        # check type casting
        if ssplit[1] == "as":
            return _decode_type_cast(value=value, line=line)

        # check indexing
        if ssplit[1] == "at":
            return _decode_object_indexing(value=value, line=line)

        # check object method calling
        if ssplit[1] == "from":
            return _decode_method_call(value=value, line=line)

    # check eval expresion
    used_expr = _decode_expr(value=value, line=line)

    if used_expr is not None:
        return used_expr

    # check for litteral instancing
    used_basic = _decode_basic_value(value=value)

    if used_basic is not None:
        return used_basic

    is_condition = _decode_condition(value=value, line=line)

    if is_condition is not None:
        return is_condition

    from therl.api import THERL

    # check if its another variable, then get its value
    if THERL.runtime.get(value) is not None:
        return THERL.runtime.get(value).value

    raise UnknownVariable(var_name=value, line=line)


def _decode_condition(value: str, line: int) -> bool | None:
    from therl.api import THERL

    try:
        ret = _decode_value(value=value, line=line)
        return ret
    except:
        return simpleval.simple_eval(
            value,
            names={var[0]: var[1].value for var in THERL.runtime.VARIABLES.items()},
        )


def _decode_basic_value(value: str) -> str | int | float | bool | None:
    if value.strip()[0] == value.strip()[-1] == '"':
        return str(value[1:-1])

    if value.strip().lower() == "true":
        return True
    if value.strip().lower() == "false":
        return False

    # Try Integer
    try:
        return int(value)
    except ValueError:
        pass

    # Try Float
    try:
        return float(value)
    except ValueError:
        pass


def _decode_expr(value: str, line: int) -> Any | None:
    import therl.consts
    from therl.api import THERL

    used_operator = not set(value.split(" ")).isdisjoint(therl.consts.OPERATORS)

    if used_operator:
        try:
            return simpleval.simple_eval(
                expr=value,
                names={var[0]: var[1].value for var in THERL.runtime.VARIABLES.items()},
            )
        except NameError as e:
            raise UnknownVariable(var_name=e.name, line=line)


def _decode_run_instruction(value: str, line: int) -> Any:
    from therl.api import THERL
    from therl.instructions import RUN

    func_string = value.split("run", maxsplit=2)[1].strip()

    if "from" in func_string.split(" "):

        slices = func_string.split("from")
        var_name = slices[1].strip()
        method = slices[0].strip()

        exists = THERL.runtime.get(var_name=var_name)

        if exists is None:
            raise UnknownVariable(var_name=var_name, line=line)
        try:
            return getattr(exists, method)()
        except AttributeError:
            raise UnknownAttribute(
                object_name=var_name.capitalize(), attr_name=method, line=line
            )
    else:
        return RUN(func_string)


def _decode_type_cast(value: str, line: int) -> int | float | str | list:

    from therl.api import THERL

    slices = value.split("as")

    var_name = slices[0].strip()
    cast_to_type = slices[1].strip()

    exists = THERL.runtime.get(var_name=var_name)

    cast_value = exists.value if exists else _decode_value(var_name)

    try:
        match cast_to_type:
            case "int":
                return int(cast_value)

            case "float":
                return float(cast_value)

            case "string":
                return str(cast_value)

            case "array":
                return list(cast_value)

            case _:
                raise InvalidKeyword(
                    wrong_keyword=cast_to_type,
                    supposed_keyword="int, float, string, array",
                    line=line,
                )
    except ValueError:
        raise InvalidVariableCasting(
            wrong_type=cast_to_type,
            originial_type=exists.type.__name__,
            line=line,
        )


def _decode_object_indexing(value: str, line: int) -> Any:
    from therl.api import THERL

    slices = value.split("at")
    var_name_or_list_exp = slices[0].strip()

    index = _decode_value(slices[1].strip(), line=line)
    if not isinstance(index, int):
        raise InvalidType(
            wrong_type=type(index).__name__,
            supposed_type=int.__name__,
            line=line,
        )

    var = THERL.runtime.get(var_name_or_list_exp)

    if var is not None:

        if not isinstance(var.value, (list, str)):
            raise InvalidType(
                supposed_type="array or str",
                wrong_type=var.type.__name__,
                line=line,
            )
        try:
            return var.value[index]
        except IndexError:
            raise IndexOutOfRange(index=index, max_index=len(var.value), line=line)

    array = _decode_array(var_name_or_list_exp, line=line)

    if not isinstance(array, (list, str)):
        raise InvalidType(
            supposed_type="array or str",
            wrong_type=var.type.__name__,
            line=line,
        )
    try:
        return array[index]
    except IndexError:
        raise IndexOutOfRange(index=index, max_index=len(array) - 1, line=line)


def _decode_method_call(value: str, line: int) -> Any:

    from therl.api import THERL

    slices = value.split("from")
    var_name = slices[1].strip()
    method = slices[0].strip()

    exists = THERL.runtime.get(var_name=var_name)

    if exists is None:
        raise UnknownVariable(var_name=var_name, line=line)
    try:
        return getattr(exists, method)
    except AttributeError:
        raise UnknownAttribute(
            object_name=var_name.capitalize(), attr_name=method, line=line
        )


def _decode_array(array_str: str, line: int = 1) -> list[Any]:
    clean_str = array_str[1:-1]  # remove [ ]

    if clean_str.strip() == "":
        return []

    if ".." in clean_str:
        s_and_f = clean_str.split("..")

        try:
            start = _decode_value(s_and_f[0])
        except ValueError:
            raise InvalidType(
                supposed_type=int.__name__, wrong_type=type(start).__name__, line=line
            )
        try:
            finish = _decode_value(s_and_f[-1])
            return list(range(start, finish + 1))
        except (ValueError, TypeError):
            raise InvalidType(
                supposed_type=int.__name__,
                wrong_type=type(finish).__name__,
                line=line,
            )
    array = []

    for val in clean_str.split(","):
        v = _decode_value(val.strip())
        if len(array) > 0 and type(array[0]) != type(v):
            raise InvalidType(
                supposed_type=type(array[0]).__name__,
                wrong_type=type(v).__name__,
                line=line,
            )

        array.append(v)

    return array
