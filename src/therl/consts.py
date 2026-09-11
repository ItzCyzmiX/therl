import re

from therl.instructions import RETURN, RUN, SAY, SET, INPUT

OPERATORS = ["+", "-", "/", "*", "**"]
INSTRUCTIONS_KEYWORDS = sorted(
    [
        "set",
        "say",
        "func",
        "end",
        "run",
        "return",
        "if",
        "foreach",
        "while",
        "else",
        "elseif",
        "break",
        "continue",
        "input",
    ],
    key=len,
    reverse=True,
)
INSTRUCTION_TO_FUNC = {
    "say": SAY,
    "set": SET,
    "run": RUN,
    "return": RETURN,
    "input": INPUT,
}
pattern = f"({'|'.join(map(re.escape, INSTRUCTIONS_KEYWORDS))})"
params_pattern = f"({'|'.join(map(re.escape, ['<', '>']))})"
