import re

from .instructions import ADD, CAST, RETURN, RUN, SAY, SET

OPERATORS = ["+", "-", "/", "*", "**"]
INSTRUCTIONS_KEYWORDS = sorted(
    ["add", "set", "say", "cast", "func", "eof", "run", "return"],
    key=len,
    reverse=True,
)
INSTRUCTION_TO_FUNC = {
    "say": SAY,
    "set": SET,
    "cast": CAST,
    "add": ADD,
    "run": RUN,
    "return": RETURN,
}
pattern = f"({'|'.join(map(re.escape, INSTRUCTIONS_KEYWORDS))})"
params_pattern = f"({'|'.join(map(re.escape, ['<', '>']))})"
