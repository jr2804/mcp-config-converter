# Python Development, Guidelines and Best Practices

## Usage of uv and Project Environment Management

- Use `uv` for creating isolated Python environments instead of `virtualenv` or `venv`. This ensures consistency across different development setups and simplifies dependency management.
- Use `uv` for managing project dependencies and ensuring reproducibility across different environments.
- Use `uv` for running Python scripts within the isolated environment to ensure that the correct dependencies are used.
- Use `uv` for packaging and distributing Python applications to ensure that all dependencies are included and the application can be easily installed in different environments.
- Use `uv` for managing project configurations and settings.
- Use `uv` for running tests to ensure that the correct dependencies and configurations are used.
- Use `uv` for all package management. Never use `pip` directly.
- Use `uv add <package>` for adding new dependencies to your project.
- Use `uv remove <package>` for removing dependencies from your project.
- Use `uv sync --all-extras -U` for a full update of all dependencies, including optional extras.
- Use `uv add <package> --dev` for adding new development dependencies to your project. Do not use `project.optional-dependencies.test` in `pyproject.toml`.
- Use `uv remove <package> --dev` for removing development dependencies from your project.
- Use `uv run <script>` for running Python scripts within the isolated environment. Never use `<some_path>/python <script.py> <arguments>` directly!
- Use `uv run python -c"<code>"` for running Python scripts within the isolated environment. Never use `<some_path>/python -c"<code>"` directly!
- Use `uv run pytest` for running tests to ensure that the correct dependencies and configurations are used.
- Use `uv build` for packaging and distributing Python applications to ensure that all dependencies are included and the application can be easily installed in different environments.
- Add/install packages like `pytest`, `ruff`, etc., as development dependencies using `uv add <package> --dev`.

## Variables and Naming Conventions

- Use clear and descriptive names for variables, functions, classes, and modules.
- Follow the PEP 8 naming conventions for Python code (e.g., `snake_case` for variables and functions, `PascalCase` for classes).
- Avoid using single-letter variable names, except for loop counters or mathematical variables (e.g., `i`, `j`, `x`, `y`).
- Avoid using abbreviations or acronyms unless they are widely recognized and understood.
- Use consistent naming conventions throughout the codebase.
- Use meaningful names that convey the purpose or intent of the variable/function/class/module.
- Avoid using names that are too generic or vague (e.g., `data`, `info`, `temp`).
- Use names that are easy to read and understand, avoiding overly complex or convoluted names.
- Use names that are consistent with the domain or context of the project.
- Avoid using names that are too similar to each other, which can lead to confusion.
- When in doubt, choose clarity over brevity.
- Use constants for values that are used multiple times throughout the codebase.
- For constants, use `UPPER_SNAKE_CASE` naming convention.
- Avoid using magic numbers or strings in the code. Instead, define them as constants with meaningful names.
- Use enums for sets of related constants that represent a specific type or category.
- Use type hints to indicate the expected types of variables, function parameters, and return values.
- For variables or arguments indicating a filename, use `snake_case` with a `_file` suffix (e.g., `input_file`, `output_file`).
- For variables or arguments indicating a directory path, use `snake_case` with a `_dir` suffix (e.g., `input_dir`, `output_dir`).
- Never use the suffix `_dir` for filename variables or arguments, as it might be confused with directory paths.
- Never use the suffix `_file` for directory path variables or arguments, as it might be confused with filenames.
- Use the suffix `_path` **only in very rare, exceptional cases** for naming directory or filename variables or arguments, as it remains unclear whether it indicates a file or directory. Always prefer `_file` or `_dir` instead.

## Python-Specific Guidelines

After implementing a new feature or making significant changes, ensure code quality and consistency by running our standard tools (`ruff`, `ty`, `undersort`, `isort`) and checking for violations of `ruff` rule [`TRY003`](https://docs.astral.sh/ruff/rules/raise-vanilla-args), which flags exception messages that should be defined on the exception class itself. For more detailed guidance on using these tools, refer to the dedicated code-quality tooling documentation.

- Follow PEP 8 style guide for Python code.
- Follow [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for docstrings.
- Use f-strings for formatting strings.
- Use list comprehensions and dictionary comprehensions where appropriate.
- Never use the obsolete type hint `x: Optional[SomeType] = None`! Instead, always use `x: SomeType | None = None`.
- Use `is` and `is not` for comparing to `None`, not `==` or `!=`.
- Use `enumerate()` when you need both the index and the value in a loop.
- Use `with` statements when working with files to ensure proper resource management.
- Use `rich.console.Console` for CLI output instead of `print()` or `logging` for user-facing messages.
- Use basic Python types and NumPy arrays for data structures. Use `pydantic` only if complex data validation is needed.
- Avoid hard-coding of constant expressions, in particular these of type `str`, `int`, `float`, and `bool`. Instead, define them as named constants at the top of the module or in a separate `constants.py` module (either globally or locally/per submodule).

### Python-Specific Guidelines for Files and Directories

- Use `pathlib` module for file system paths.
- **Never** store file names or directory names as strings or use string manipulation for paths.
- **Never** use `os.path` instead of `pathlib`.
- Use `pathlib.Path` class for all file names, directory names and any path manipulations.

### Python-Specific Guidelines for Type Hinting

- Use `typing` module for type annotations.
- Use type hints everywhere, including for function parameters and return values. Use generics where appropriate.
- Avoid `typing.Optional` for optional values, use `SomeType | None` instead.
- Do **not** use `typing.Union` for multiple possible types, use `SomeType | AnotherType` instead.
- Use `typing.TypeVar` for generic types.
- Use `typing.Protocol` for defining interfaces.
- Do **not** use `typing.List`, `typing.Dict`, `typing.Set`, or `typing.Tuple`. Instead, use built-in generic types like `list`, `dict`, `set`, and `tuple` with type parameters (e.g., `list[int]`, `dict[str, float]`).

### Python-Specific Guidelines for Tools

- Use `ruff` for code formatting.
- Use `isort` for sorting imports.
- Use `undersort` for sorting methods in classes.
- Use `pytest` for testing (see also next sections).
- Use `ty` for type checking (see also next section).
- Use `deptry` for dependency analysis.

### Python-Specific Guidelines for Type Checking

- Use `ty` for type checking only.
- Do **not** use `mypy` or add any code specifically for type checking with `mypy`.
- Configure `ty` via `pyproject.toml` only.
- Try to avoid the idiom `from typing import TYPE_CHECKING` whenever possible. Use it only to avoid circular references.

### Python-Specific Guidelines for Import Style

**Always use absolute imports** throughout the project, with one exception for `__init__.py` files:

```python
# ✅ CORRECT - Absolute imports in regular modules
from module.common.types import TestDesign
from module.consolidate.parsing import parse_p800_raw_results

# ❌ AVOID - Relative imports in regular modules
from .types import TestDesign
from ..consolidate.parsing import parse_p800_raw_results

# ✅ EXCEPTION - Relative imports allowed in __init__.py files only
# (for collecting/re-exporting from submodules)
from .parsing import parse_p800_raw_results
from .statistics import calculate_mos_statistics
from .p800 import consolidate_p800_results
```

**Rationale:**

- Explicit and clear about module location
- Easier to search and refactor
- Prevents ambiguity in nested package structures
- Consistent with project structure documentation
- `__init__.py` files use relative imports for brevity when re-exporting from their own submodules

### Python-Specific Guidelines for Reading/Writing tabular data

- For reading/writing data from/to CSV and Excel files, use `pandas`.
  - Use the engine from `python-calamine` for reading Excel files.
  - Use the engine from `xlsxwriter` for writing Excel files.
  - For performance reasons, **never** use `openpyxl` to read or write Excel files!
  - Do not specify the engines explicitly when writing or reading Excel files with `pandas.read_excel()` / `pandas.Dataframe.to_excel()`, as `python-calamine` and `xlsxwriter` are defined as the default engine via hard-coded statements in `/<package>/__init__.py`.

## Refactoring Triggers

When size limits are exceeded during implementation:

1. **Modules (single .py files) > 250 lines:** If a module exceeds this limit, decide between two options:

   - Refactor it into (at least two) new module(s) and extract related functions into separate modules, or:
   - Create new submodule directory with split functionality. Extract related functions into separate modules. Use `__init__.py` to expose public API.

1. **Single function (declaration + implementation) > 75 lines:** Extract helper functions or decompose into smaller functions.

   - Identify logical sub-steps in the function
   - Extract helper functions for reusable logic
   - Use descriptive function names for clarity

1. **Classes (declaration + implementation) > 200 lines:** Apply SRP, consider mixins, or use functional approach

   - Split responsibilities into multiple smaller classes
   - Consider composition over inheritance
   - Use mixins for shared behavior
   - If the class has too many methods operating on different data, use functional programming

## Module and Class Guidelines

Prefer module-level functions for simple utilities. Use classes with static methods when you need:

- Shared class variables
- Logical grouping of related static operations
- Clear namespace separation for cohesive functionality

If a class has too many methods, consider splitting it into multiple smaller classes with single responsibility. If a class has too many attributes, consider using composition instead of inheritance. If a class has too many responsibilities, consider using the Single Responsibility Principle (SRP) to refactor it into smaller classes or using mixins. If a class has too many dependencies, consider using dependency injection to reduce coupling. If a class has too many methods that operate on the same data, consider using the Data Transfer Object (DTO) pattern to encapsulate the data. If a class has too many methods that operate on different data, consider using the Strategy pattern to encapsulate the different behaviors. If a class gets too complex and/or the interaction between other objects becomes convoluted, consider using functional programming instead of object-oriented programming style.

After implementing a new feature or making significant changes, run `ruff`, `ty`, `undersort` and `isort` to ensure code quality and consistency. Check for violations against `ruff` rule [`TRY003`](https://docs.astral.sh/ruff/rules/raise-vanilla-args), which checks for (long) exception messages that are not defined in the exception class itself. Avoid **at all cost** the use of (hidden) inline imports! Always place imports at the top of the module, unless there is a very good reason not to do so (e.g., to avoid circular dependencies). If you find yourself needing inline imports frequently, consider refactoring the code to eliminate the need for them.

When renaming or moving Python modules (files or directories), use tool `git mv <source> <destination>`. See [text](https://git-scm.com/docs/git-mv) for details.

## Technical Requirements

## Guidelines for Literal Strings

- For multi-line strings NEVER put multi-line strings flush against the left margin.
  ALWAYS use a `dedent()` function to make it more readable.
  You may wish to add a `strip()` as well.
  Example:

  ```python
  from textwrap import dedent
  markdown_content = dedent("""
      # Title 1
      Some text.
      ## Subtitle 1.1
      More text.
      """).strip()
  ```

## Guidelines for Backward Compatibility

- When changing code in a library or general function, if a change to an API or library
  will break backward compatibility, MENTION THIS to the user.
- DO NOT implement additional code for backward compatibility (such as extra methods or
  variable aliases or comments about backward compatibility) UNLESS the user has
  confirmed that it is necessary.
