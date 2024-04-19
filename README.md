<div align="center">

# Gem Hunter

### An agent that attempts to solve a modified version of Minesweeper, while there are gems to excavate.

</div>

## Description

A project that aims to create an agent, that can solve this specific rendition of Minesweeper, titled Gem Hunter. The agent needs to be able to accept an input, that looks like a grid with numbers, and missing cells, and able to reason out which cells are safe to excavate (gems), and which cells are not safe to excavate (mines or traps).

Main collaborators:

- [@sytanl](https://github.com/sytanl)
- [@xiao-honsu](https://github.com/xiao-honsu)
- [@khahhy](https://github.com/khahhy)
- [Me](https://github.com/hikawi)

## Getting Started

To get started, there are packages that need to be installed. You can install them yourself:

- `numpy` for representing data similar to array languages. Could be needed for representing the grid.
- `python-sat` for solving the CNFs. (my bad, I thought `pysat` was it, but `pysat` is for _satellite data analysis_)
- `mypy` for static type checking.
- `pandas` for data frames, which may not be necessary, but good to have.

Or, you can use the listed `requirements.txt` file to install the packages:

```bash
pip install -r requirements.txt
```

## Contributing

The `main` branch is **protected**, which means that you cannot push directly to it. So here's a rundown on how to start working:

1. Obviously, have your own _local repo_ updated.
2. Checkout a new branch from `main` with a descriptive name, can be what you're working on, or just a variation of your name (`board-randomizer`, `sytanl-dev`, etc.).
3. Change whatever you want. Do your work.
4. When done, commit and push your changes to the remote repo, with the **same branch name**.
5. Create a [pull request](https://github.com/hikawi/gem-hunter/pulls) **from** your branch **to** `main`.
6. Wait for me to review (so VHD can't break it) before merging into the main branch.

**Do not**, (YOU VHD), commit environment files. For example, `.vscode`, `.idea`, `__pycache__`, `.mypy_cache`, `.venv`, etc. When adding files to commit, do not use `git add .`. Instead, use `git add <specific files>`.

## Code Style

I settle on always `lower_case` for variables, functions, methods and modules. `UPPER_CASE` for constants, and `PascalCase` for classes. If you have something that you do not want others to use, prefix it with an underscore `_`. When you write anything, _comment_. Comment **what** and **why** you are doing that.

<details>

<summary>Example File</summary>

Although not recommended, if a type is way too difficult to know, you may use `Any` from module `typing`. But try to avoid it as much as possible.

```python
# A constant number that does nothing, there's no reason for it.
CONSTANT_NUMBER = 42

def fib(n: int) -> int:
    """
    Calculates the nth Fibonacci number.
    """
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

def long_function_that_does_nothing(a: int, b: int, c: float) -> None:
    """
    This function does nothing, but it's long.
    """
    c: int = a + b
    d: float = c * 2
    e: float = c + d

    # A variable that has its type easy to see doesn't need typing.
    big_variable_that_sums_all = a + b + c + d + e         # BAD! Mix of int and float.
    _dont_touch_this = "Please don't touch this string"    # GOOD! Everyone knows it's a string.

list_of_ints: list[int] = [1, 2, 3, 4, 5]
list_of_floats: list[float] = [1.0, 2.0, 3.0, 4.0, 5.0]

import typing
actual_unknown_variable_with_no_types: typing.Any = 69

class HelloWorld:
    """
    A class that prints Hello.
    """

    def hello(self, someone: str) -> None:
        """
        Prints Hello to someone.
        """
        print(f"Hello, {someone}!")
```

</details>

## Data Representation

Data will be represented as a number grid, with the following rules:

- _Any number_ >= 0 represents the number of **mines** around that cell.
- A number `-1` represents a **mine**.
- A number `-2` represents a **gem**.
- A number `-3` represents an **unknown** cell.
