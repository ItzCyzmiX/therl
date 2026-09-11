# Therl examples

Run an example from the project root with:

```text
python -m therl examples/variables.therl
```

The examples cover the core language features:

- `variables.therl` - scalar values, lists, reassignment, and indexing
- `conditionals.therl` - `if`, `elseif`, and `else`
- `functions.therl` - function parameters, calls, and return values
- `foreach.therl` - iterating over a list and a string
- `while.therl` - repeating while a condition is true
- `casting.therl` - converting values with `as int`, `as float`, `as string`, and `as array`
- `input.therl` - reading user input into a variable
- `type_safety.therl` - an intentional error showing that reassignment keeps the original type

`type_safety.therl` should fail with an `Invalid type` error because `score` starts as an integer and is later assigned a string.
