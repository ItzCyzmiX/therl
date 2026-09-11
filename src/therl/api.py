import re
from typing import Any

from therl.consts import INSTRUCTION_TO_FUNC, params_pattern, pattern
from therl.error import (
    InfiniteLoop,
    InvalidType,
    NameInUse,
    UnknownInstruction,
)
from therl.functions import Function
from therl.utils import _decode_condition, _decode_value
from therl.variable import Variable


class Runtime:
    def __init__(self, variables: dict[str, Variable] = {}):
        self.VARIABLES = variables

    def get(self, var_name: str) -> Variable | None:
        return self.VARIABLES.get(var_name)

    def set(self, var_name: str, value: Any, line: int = 0):
        var = self.VARIABLES.get(var_name)
        if var:
            var.set(value, line)

    def new(self, var_name: str, value: Any, line: int = 0):

        self.VARIABLES[var_name] = Variable(name=var_name, value=value, line=line)

    def delete(self, var_name: str):
        var = self.VARIABLES.get(var_name)
        if var:
            del self.VARIABLES[var_name]

    def change_at_index(self, var_name: str, index: int, value: Any):
        self.VARIABLES[var_name][index] = value

    def new_object(self, obj_name: str, object: Variable):
        self.VARIABLES[obj_name] = object


class Therl:
    def __init__(self, globals: dict[str, Variable] = {}):
        self.runtime = Runtime(variables=globals)

    def register_object(self, object: Variable):
        self.runtime.new_object(obj_name=object.name, object=object)

    def run(self, code: str, starting_line_num: int = 0):
        """[instruction string, line number (for errors)]"""

        instructions = [
            [line.strip(), line_num + starting_line_num + 1]
            for line_num, line in enumerate(code.split("\n"))
            if line.strip()
        ]

        i = 0
        cur_conditions_met: list[bool] = []
        skip = False
        while i < len(instructions):
            instruction = instructions[i]

            tokens = [
                t.strip() for t in re.split(pattern, instruction[0], maxsplit=1) if t
            ]

            action = tokens[0]
            arg = "".join(tokens[1:])

            if action == "if":
                condition = tokens[1]

                cur_conditions_met.append(
                    _decode_condition(value=condition, line=instruction[1])
                )

            elif action == "elseif":
                if cur_conditions_met[-1]:
                    skip = True
                elif cur_conditions_met and not cur_conditions_met[-1]:
                    condition = tokens[1]

                    cur_conditions_met[-1] = _decode_condition(
                        value=condition, line=instruction[1]
                    )

            elif action == "else":
                if cur_conditions_met:
                    cur_conditions_met[-1] = not cur_conditions_met[-1]

            elif action == "end":
                if cur_conditions_met:
                    cur_conditions_met.pop()

            elif action == "foreach":
                var_name, iterator_str = [_.strip() for _ in arg.strip().split("in", 1)]

                iterator = _decode_value(iterator_str)

                if not isinstance(iterator, (list, str)):
                    raise InvalidType(
                        "array or string", type(iterator).__name__, instruction[1]
                    )

                self.runtime.new(var_name, iterator[0], instruction[1])

                start_line_num = instructions[i][1] + 1

                i += 1  # ← Move to first instruction inside the loop
                depth = 1
                code_str = ""
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

                    code_str += instruction[0] + "\n"

                    if depth <= 0:
                        for x in iterator:
                            self.runtime.set(var_name, x, instruction[1])

                            b_or_c = self.run(code_str, start_line_num)

                            if b_or_c == "break":
                                break

                            if b_or_c == "continue":
                                continue

                        self.runtime.delete(var_name)

                        break

                    i += 1

            elif action == "while":
                condition_str = arg.strip()

                condition = _decode_condition(condition_str, instructions[i][1])

                start_line_num = instructions[i][1] + 1

                i += 1  # ← Move to first instruction inside the loop
                depth = 1
                code_str = ""
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

                    code_str += instruction[0] + "\n"

                    if depth <= 0:
                        try:
                            while condition:
                                b_or_c = self.run(code_str, start_line_num)

                                if b_or_c == "break":
                                    break

                                condition = _decode_condition(
                                    condition_str, instructions[i][1]
                                )

                                if b_or_c == "continue":
                                    continue

                                if not condition:
                                    break
                        except RecursionError:
                            raise InfiniteLoop(
                                loop_type="while", line=start_line_num - 1
                            )

                        break

                    i += 1

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
                    if not skip:
                        if not cur_conditions_met or all(cur_conditions_met):
                            if action == "return":
                                return INSTRUCTION_TO_FUNC[action](arg, instruction[1])
                            elif action == "break":
                                return "break"
                            elif action == "continue":
                                return "continue"

                            INSTRUCTION_TO_FUNC[action](arg, instruction[1])
                    else:
                        skip = False
                except KeyError:
                    raise UnknownInstruction(
                        instruction_name=action, line=instruction[1]
                    )

            i += 1


THERL = Therl()
