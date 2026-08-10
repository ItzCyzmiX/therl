import sys
from typing import Any

from therl.variable import Variable


class Runtime:
    def __init__(self, variables: dict[str, Variable] = {}):
        self.VARIABLES = variables

    def get(self, var_name: str) -> Variable | None:
        return self.VARIABLES.get(var_name)

    def set(self, var_name: str, value: Any):
        var = self.VARIABLES.get(var_name)
        if not var:
            print(f"Variable named {var_name} doesnt exist")
            sys.exit(1)

        var.set(value)

    def new(self, var_name: str, value: Any):
        if self.VARIABLES.get(var_name) is not None:
            print(f"Variable named {var_name} already exists")
            sys.exit(1)

        self.VARIABLES[var_name] = Variable(name=var_name, value=value)

    def new_object(self, obj_name: str, object: Variable):
        if self.VARIABLES.get(var_name) is not None:
            print(f"Object named {var_name} already exists")
            sys.exit(1)

        self.VARIABLES[var_name] = object


class Therl:
    def __init__(self, globals: dict[str, Variable] = {}):
        self.runtime = Runtime(variables=globals)

    def register_object(self, name: str, object: Variable):
        self.runtime.new_object(obj_name=name, object=object)


therl = Therl()
