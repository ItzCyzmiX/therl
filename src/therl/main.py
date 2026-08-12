import sys
from therl.api import THERL


def main():
    # sys.excepthook = lambda type, value, traceback: print(
    #     f"{type.__name__} Error:\n\n{value}"
    # )

    code_str = ""

    try:
        if sys.argv[1].split(".")[-1] != "therl":
            print("Invalid file type, file must be .therl")
            sys.exit(1)

        with open(sys.argv[1], "r") as file:
            code_str = file.read()
    except IndexError:
        print("no file provided!")
        sys.exit(1)
    except FileNotFoundError:
        print("file doesnt exist!")
        sys.exit(1)

    THERL.run(code=code_str)
