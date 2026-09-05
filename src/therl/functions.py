from typing import Any

from therl.types import VARIABLES_TYPE


class Function:
    def __init__(
        self,
        name: str,
        params: list[str],
        instructions: list[tuple[list[str], int]] | None = None,
    ) -> None:
        self.instructions = instructions
        self.name = name
        self.params = params

    def __str__(self) -> str:
        return f"function: {self.name}"

    def run(self, params: VARIABLES_TYPE | None = None) -> Any | None:
        from therl.api import THERL

        if self.instructions is None:
            return

        OG_VARS = THERL.runtime.VARIABLES.copy()
        THERL.runtime.VARIABLES = THERL.runtime.VARIABLES | (params or {})

        return_value = THERL.run(
            "\n".join([(" ".join(x[0])) for x in self.instructions]),
            starting_line_num=self.instructions[0][1] - 1,
        )

        if return_value is not None:
            THERL.runtime.VARIABLES = OG_VARS
            return return_value

        THERL.runtime.VARIABLES = OG_VARS
