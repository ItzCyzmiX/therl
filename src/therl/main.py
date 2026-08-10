import re
import sys

from therl.consts import INSTRUCTION_TO_FUNC, params_pattern, pattern
from therl.functions import Function
from therl.runtime import VARIABLES
from therl.variable import Variable


def main():
    sys.excepthook = lambda type, value, traceback: print(
        f"{type.__name__} Error:\n\n{value}"
    )
    try:
        if sys.argv[1].split(".")[-1] != "therl":
            print("Invalid file type, file must be .therl")
            sys.exit(1)

        with open(sys.argv[1], "r") as file:
            instructions = [
                [line.strip(), line_num + 1]
                for line_num, line in enumerate(file)
                if line.strip()
            ]
    except IndexError:
        print("no file provided!")
        sys.exit(1)
    except FileNotFoundError:
        print("file doesnt exist!")
        sys.exit(1)

    inside_function = False
    cur_func_instuctions = []
    cur_func_name = ""
    cur_func_params = set()

    for instruction in instructions:
        tokens = [t.strip() for t in re.split(pattern, instruction[0], maxsplit=1) if t]

        action = tokens[0]

        arg = "".join(tokens[1:])

        if action == "eof":
            inside_function = False

            VARIABLES[cur_func_name] = Variable(
                name=cur_func_name,
                value=Function(
                    name=cur_func_name,
                    instructions=cur_func_instuctions,
                    params=list(cur_func_params),
                ),
            )
            cur_func_name = ""
            cur_func_instuctions = []
            cur_func_params.clear()
            continue

        if inside_function:
            cur_func_instuctions.append(tokens)
            continue

        if action == "func":
            name_and_params = [l.strip() for l in arg.split(" ") if l]
            cur_func_name = name_and_params[0]

            if VARIABLES.get(cur_func_name) is not None:
                print(
                    f"Cant name function to a variable of the same name, '{cur_func_name}' is already defined!"
                )
                sys.exit(1)

            inside_function = True
            params_split = [
                t.strip()
                for t in re.split(params_pattern, "".join(name_and_params[1:]))
                if t
            ]
            for i, param in enumerate(params_split):
                try:
                    if param == "<" and params_split[i + 2] == ">":
                        cur_func_params.add(params_split[i + 1])
                except IndexError:
                    break

        if not inside_function:
            INSTRUCTION_TO_FUNC[action](arg, instruction[1])
