# Project-Specific Development Rules

> **Note:** For universal Python guidelines, UV usage, type hints, and coding principles, refer to the skills in `.claude/skills/development/`:
>
> - [python_guidelines](../../.claude/skills/development/python_guidelines/SKILL.md) - Python best practices, type hints, imports
> - [uv_mcp](../../.claude/skills/development/uv_mcp/SKILL.md) - UV package management workflows
> - [coding_principles](../../.claude/skills/development/coding_principles/SKILL.md) - Version control, code quality, comments

## Project-Specific Rules

### Refactoring Triggers

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

### Multi-line String Formatting

For multi-line strings NEVER put them flush against the left margin. ALWAYS use a `dedent()` function to make it more readable. You may wish to add a `strip()` as well.

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

### Backward Compatibility

When changing code in a library or general function, if a change to an API or library will break backward compatibility, **MENTION THIS to the user**.

DO NOT implement additional code for backward compatibility (such as extra methods or variable aliases or comments about backward compatibility) UNLESS the user has confirmed that it is necessary.

### Excel File Handling

For reading/writing data from/to CSV and Excel files, use `pandas`:

- Use the engine from `python-calamine` for reading Excel files
- Use the engine from `xlsxwriter` for writing Excel files
- For performance reasons, **never** use `openpyxl` to read or write Excel files!
- Do not specify the engines explicitly when writing or reading Excel files with `pandas.read_excel()` / `pandas.DataFrame.to_excel()`, as `python-calamine` and `xlsxwriter` are defined as the default engine via hard-coded statements in `/<package>/__init__.py`

### Module Renaming/Moving

When renaming or moving Python modules (files or directories), use tool `git mv <source> <destination>`. See [git-mv documentation](https://git-scm.com/docs/git-mv) for details.

### Exception Message Rule

After implementing a new feature or making significant changes, check for violations against `ruff` rule [`TRY003`](https://docs.astral.sh/ruff/rules/raise-vanilla-args), which checks for (long) exception messages that are not defined in the exception class itself.
