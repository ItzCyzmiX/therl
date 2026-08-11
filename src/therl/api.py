import sys
from typing import Any
import re
from therl.variable import Variable

from therl.consts import pattern, params_pattern, INSTRUCTION_TO_FUNC
from therl.functions import Function


class Runtime:
    def __init__(self, variables: dict[str, Variable] = {}):
        self.VARIABLES = variables

    def get(self, var_name: str) -> Variable | None:
        return self.VARIABLES.get(var_name)

    def set(self, var_name: str, value: Any):
        var = self.VARIABLES.get(var_name)
        if not var:
            print(f"Variable named {var_name} doesnt exist")
            sys.exit(1)

        var.set(value)

    def new(self, var_name: str, value: Any):
        self.VARIABLES[var_name] = Variable(name=var_name, value=value)

    def change_at_index(self, var_name: str, index: int, value: Any):
        self.VARIABLES[var_name][index] = value

    def new_object(self, obj_name: str, object: Variable):
        self.VARIABLES[obj_name] = object


class Therl:
    def __init__(self, globals: dict[str, Variable] = {}):
        self.runtime = Runtime(variables=globals)

    def register_object(self, name: str, object: Variable):
        self.runtime.new_object(obj_name=name, object=object)

    def run(self, code: str):

        inside_function = False

        cur_func_instuctions = []
        cur_func_name = ""
        cur_func_params = set()

        instructions = [
            [line.strip(), line_num + 1]
            for line_num, line in enumerate(code.split("\n"))
            if line.strip()
        ]  # [instruction string, line number (for errors)]

        for instruction in instructions:
            tokens = [
                t.strip() for t in re.split(pattern, instruction[0], maxsplit=1) if t
            ]

            action = tokens[0]

            arg = "".join(tokens[1:])

            if action == "eof":
                inside_function = False

                self.runtime.new(
                    cur_func_name,
                    Function(
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

                if self.runtime.get(cur_func_name) is not None:
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


THERL = Therl()
