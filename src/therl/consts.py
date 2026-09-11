import re

from therl.instructions import RETURN, RUN, SAY, SET

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
    ],
    key=len,
    reverse=True,
)
INSTRUCTION_TO_FUNC = {
    "say": SAY,
    "set": SET,
    "run": RUN,
    "return": RETURN,
}
pattern = f"({'|'.join(map(re.escape, INSTRUCTIONS_KEYWORDS))})"
params_pattern = f"({'|'.join(map(re.escape, ['<', '>']))})"
