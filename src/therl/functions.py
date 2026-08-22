import sys
from typing import Any
import re
from therl.error import UnknownInstruction
from therl.types import VARIABLES_TYPE
from therl.utils import _decode_condition
from therl.consts import pattern


class Function:
    def __init__(
        self,
        name: str,
        params: list[str],
        instructions: list[str] | None = None,
    ) -> None:
        self.instructions = instructions
        self.name = name
        self.params = params

    def __str__(self):
        return f"function: {self.name}"

    def run(self, params: VARIABLES_TYPE | None = None) -> Any:
        from therl.api import THERL
        from therl.consts import INSTRUCTION_TO_FUNC

        if self.instructions is None:
            return

        THERL.runtime.VARIABLES = THERL.runtime.VARIABLES | (params or {})
        i = 0
        cur_conditions_met: list[bool] = []

        while i < len(self.instructions):
            instruction = self.instructions[i]

            action = instruction[0][0]

            if action == "if":
                condition = instruction[0][1]

                cur_conditions_met.append(
                    _decode_condition(value=condition, line=instruction[1])
                )

            elif action == "else":
                if cur_conditions_met:
                    cur_conditions_met[-1] = not cur_conditions_met[-1]

            elif action == "end":
                if cur_conditions_met:
                    cur_conditions_met.pop()

            elif action == "return":

                return INSTRUCTION_TO_FUNC[action](instruction[0][1], instruction[1])
            else:
                try:
                    if not cur_conditions_met or all(cur_conditions_met):
                        INSTRUCTION_TO_FUNC[action](instruction[0][1], instruction[1])
                except (KeyError, IndexError):
                    raise UnknownInstruction(
                        instruction_name=action, line=instruction[1]
                    )
            i += 1
