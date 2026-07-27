import re

from .instructions import ADD, CAST, RUN, SAY, SET

OPERATORS = ["+", "-", "/", "*", "**"]
INSTRUCTIONS_KEYWORDS = sorted(
    ["add", "set", "say", "cast", "func", "eof", "run"],
    key=len,
    reverse=True,
)
INSTRUCTION_TO_FUNC = {"say": SAY, "set": SET, "cast": CAST, "add": ADD, "run": RUN}
pattern = f"({'|'.join(map(re.escape, INSTRUCTIONS_KEYWORDS))})"
params_pattern = f"({'|'.join(map(re.escape, ['<', '>']))})"
