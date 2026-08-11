import sys
from therl.api import THERL
from therl.variable import Variable


class Player(Variable):
    def __init__(self):
        self.hp = 100
        super().__init__(name="player", value=self)

    def hurt(self, amount: int):
        self.hp -= amount

    def heal(self, amount: int):
        self.hp += amount


def main():
    sys.excepthook = lambda type, value, traceback: print(
        f"{type.__name__} Error:\n\n{value}"
    )

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

    THERL.runtime.new_object("player", Player())

    THERL.run(code=code_str)
