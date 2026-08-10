import sys
from typing import Any

from therl.types import VARIABLES_TYPE


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
        import therl.runtime
        from therl.consts import INSTRUCTION_TO_FUNC

        if self.instructions is None:
            return

        therl.runtime.VARIABLES = therl.runtime.VARIABLES | (params or {})

        for instruction in self.instructions:
            action = instruction[0]

            try:
                if action == "return":
                    return INSTRUCTION_TO_FUNC[action](instruction[1])

                INSTRUCTION_TO_FUNC[action](instruction[1])
            except (KeyError, IndexError):
                print("invalid instruction:", str(instruction))
                sys.exit(1)
