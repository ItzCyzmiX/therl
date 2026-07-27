import sys

from .consts import INSTRUCTION_TO_FUNC
from .types import VARIABLES_TYPE


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

    def __name__(self):
        return "function"

    def run(self, params: VARIABLES_TYPE | None = None):
        import therl.runtime

        if self.instructions is None:
            return

        OLD_VARIABLES = therl.runtime.VARIABLES

        if params:
            therl.runtime.VARIABLES = therl.runtime.VARIABLES | params

        for instruction in self.instructions:
            action = instruction[0]

            try:
                INSTRUCTION_TO_FUNC[action](instruction[1])
                therl.runtime.VARIABLES = OLD_VARIABLES
            except (KeyError, IndexError):
                print("invalid instruction:", str(instruction))
                sys.exit(1)
