from typing import Any
import re
from therl.error import NameInUse, UnknownInstruction, UnknownVariable
from therl.utils import _decode_condition
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
        if var:
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
        """[instruction string, line number (for errors)]"""

        instructions = [
            [line.strip(), line_num + 1]
            for line_num, line in enumerate(code.split("\n"))
            if line.strip()
        ]

        i = 0
        cur_condition_met = None

        while i < len(instructions):
            instruction = instructions[i]

            tokens = [
                t.strip() for t in re.split(pattern, instruction[0], maxsplit=1) if t
            ]

            action = tokens[0]
            arg = "".join(tokens[1:])

            if action == "if":
                condition = tokens[1]
                cur_condition_met = _decode_condition(
                    value=condition, line=instruction[1]
                )
                i += 1
                instruction = instructions[i]

                tokens = [
                    t.strip()
                    for t in re.split(pattern, instruction[0], maxsplit=1)
                    if t
                ]

                action = tokens[0]
                arg = "".join(tokens[1:])

            if action == "else":
                cur_condition_met = not cur_condition_met
                i += 1
                instruction = instructions[i]

                tokens = [
                    t.strip()
                    for t in re.split(pattern, instruction[0], maxsplit=1)
                    if t
                ]

                action = tokens[0]
                arg = "".join(tokens[1:])

            if action == "end":
                if cur_condition_met is not None:
                    cur_condition_met = None

            elif action == "func":
                name_and_params = [l.strip() for l in arg.split(" ") if l]
                func_name = name_and_params[0]
                func_instructions = []
                func_params = set()

                if self.runtime.get(func_name) is not None:
                    raise NameInUse(var_name=func_name, line=instruction[1])

                params_split = [
                    t.strip()
                    for t in re.split(params_pattern, "".join(name_and_params[1:]))
                    if t
                ]
                for j, param in enumerate(params_split):
                    try:
                        if param == "<" and params_split[j + 2] == ">":
                            func_params.add(params_split[j + 1])
                    except IndexError:
                        break

                i += 1  # ← Move to first instruction inside function
                depth = 1
                while i < len(instructions):
                    instruction = instructions[i]

                    inner_tokens = [
                        t.strip()
                        for t in re.split(pattern, instruction[0], maxsplit=1)
                        if t
                    ]

                    inner_action = inner_tokens[0]

                    if inner_action in ["if", "foreach", "while"]:
                        depth += 1

                    if inner_action == "end":
                        depth -= 1

                    if depth <= 0:
                        self.runtime.new(
                            func_name,
                            Function(
                                name=func_name,
                                instructions=func_instructions,
                                params=list(func_params),
                            ),
                        )
                        break  # ← Exit the loop instead of using still_in_function

                    func_instructions.append((inner_tokens, instruction[1]))

                    i += 1
            else:
                try:
                    if cur_condition_met is None or cur_condition_met:
                        INSTRUCTION_TO_FUNC[action](arg, instruction[1])
                except KeyError:
                    raise UnknownInstruction(
                        instruction_name=action, line=instruction[1]
                    )
            i += 1

        if cur_condition_met is not None:
            print("forgot trailing if")


THERL = Therl()
