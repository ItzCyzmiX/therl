import sys
from typing import Any

from therl.error import IndexOutOfRange, InvalidType, UnknownVariable, UnknownAttribute
from therl.variable import Variable


def _decode_value(value: str, line: int = 1) -> Any:
    from therl.api import THERL

    ssplit = value.split(" ")

    if ssplit[0].strip() == "run":
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

    if "from" in ssplit:

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

    if "at" in ssplit:
        slices = value.split("at")
        var_name_or_list_exp = slices[0].strip()

        index = _decode_value(slices[1].strip(), line=line)
        if not isinstance(index, int):
            print("Indexing must be done with an int!")
            sys.exit(1)

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

    if value[0] == "[" and value[-1] == "]":
        return _decode_array(value, line=line)

    import therl.consts

    used_operator = not set(value.split(" ")).isdisjoint(therl.consts.OPERATORS)

    if used_operator:
        try:
            return eval(
                value,
                None,
                {
                    var[0]: var[1].value for var in therl.runtime.VARIABLES.items()
                },  # will it be unsafe in this case ?
            )
        except NameError as e:
            raise UnknownVariable(var_name=e.name, line=line)

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

    if THERL.runtime.get(value) is not None:
        return THERL.runtime.get(value).value

    raise UnknownVariable(var_name=value, line=line)


def _decode_array(array_str: str, line: int = 1) -> list:
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
