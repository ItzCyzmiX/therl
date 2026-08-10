import sys
from typing import Any

from therl.error import InvalidType, UnknownVariable


def _decode_value(value: str, line: int = 1) -> Any:
    import therl.runtime

    if value.split(" ")[0].strip() == "run":
        from therl.instructions import RUN

        func_string = value.split("run", maxsplit=2)[1].strip()

        return RUN(func_string)

    if "at" in value.split(" "):
        slices = value.split("at")
        var_name = slices[0].strip()

        index = _decode_value(slices[1].strip(), line=line)
        if not isinstance(index, int):
            print("Indexing must be done with an int!")
            sys.exit(1)

        var = therl.runtime.VARIABLES.get(var_name)

        if var is None:
            print(f"Variable with name {var} doesnt exist!")
            sys.exit(1)

        if not isinstance(var.value, (list, str)):
            print(f"Indexing must be done on an array or str not a {var.type.__name__}")
            sys.exit(1)
        try:
            return var.value[index]
        except IndexError:
            print("Index out of range!")
            sys.exit(1)

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
            print(f"variable nammed {e.name} doesnt exist!")
            sys.exit(1)

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

    if therl.runtime.VARIABLES.get(value) is not None:
        return therl.runtime.VARIABLES.get(value).value

    raise UnknownVariable(var_name=value, line=line)


def _decode_array(array_str: str, line: int = 1) -> list:
    clean_str = array_str[1:-1]  # remove [ ]

    if clean_str.strip() == "":
        return []

    if ".." in clean_str:
        try:
            s_and_f = clean_str.split("..")

            start = _decode_value(s_and_f[0])

            finish = _decode_value(s_and_f[-1])

            return list(range(start, finish))
        except ValueError:
            print("Array sequence must be made with two ints!")
            sys.exit(1)

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
