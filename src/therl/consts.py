import re

from therl.instructions import ADD, RETURN, RUN, SAY, SET

OPERATORS = ["+", "-", "/", "*", "**"]
INSTRUCTIONS_KEYWORDS = sorted(
    ["add", "set", "say", "func", "end", "run", "return"],
    key=len,
    reverse=True,
)
INSTRUCTION_TO_FUNC = {
    "say": SAY,
    "set": SET,
    "add": ADD,
    "run": RUN,
    "return": RETURN,
}
pattern = f"({'|'.join(map(re.escape, INSTRUCTIONS_KEYWORDS))})"
params_pattern = f"({'|'.join(map(re.escape, ['<', '>']))})"
