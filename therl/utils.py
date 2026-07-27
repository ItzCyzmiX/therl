import sys
from typing import Any

import therl.consts


def _decode_value(value: str) -> Any:
    from therl.runtime import VARIABLES

    if value[0] == "[" and value[-1] == "]":
        return _decode_array(value)

    used_operator = not set(value.split(" ")).isdisjoint(therl.consts.OPERATORS)

    if used_operator:
        try:
            return eval(
                value,
                globals={
                    var[0]: var[1].value for var in VARIABLES.items()
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

    if VARIABLES.get(value) is not None:
        return VARIABLES.get(value).value

    print("Invalid data value: ", value.strip())
    sys.exit(1)


def _decode_array(array_str: str) -> list:
    clean_str = array_str[1:-1]  # remove [ ]

    if clean_str.strip() == "":
        return []

    if ".." in clean_str:
        try:
            s_and_f = clean_str.split("..")
            start = int(s_and_f[0])

            finish = int(s_and_f[-1])

            return list(range(start, finish))
        except ValueError:
            print("Array sequence must be made with two ints!")
            sys.exit(1)

    array = []

    for val in clean_str.split(","):
        v = _decode_value(val.strip())
        if len(array) > 0 and type(array[0]) != type(v):
            print("Cannot mix and match data types in array!")
            sys.exit(1)

        array.append(v)

    return array
