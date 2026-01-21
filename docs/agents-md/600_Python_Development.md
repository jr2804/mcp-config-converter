# Python Development and Testing Guidelines

## Project-Specific Development Configurations

### Usage of uv and Project Environment Management

- Use `uv add <package> --dev` for adding new development dependencies to your project. Do not use `project.optional-dependencies.test` in `pyproject.toml`.
- Use `uv remove <package> --dev` for removing development dependencies from your project.
- Use `uv run <script>` for running Python scripts within the isolated environment. Never use `<some_path>/python <script.py> <arguments>` directly!
- Use `uv run python -c"<code>"` for running Python scripts within the isolated environment. Never use `<some_path>/python -c"<code>"` directly!

### Python-Specific Guidelines for Reading/Writing tabular data

- For reading/writing data from/to CSV and Excel files, use `pandas`.
  - Use the engine from `python-calamine` for reading Excel files.
  - Use the engine from `xlsxwriter` for writing Excel files.
  - For performance reasons, **never** use `openpyxl` to read or write Excel files!
  - Do not specify the engines explicitly when writing or reading Excel files with `pandas.read_excel()` / `pandas.Dataframe.to_excel()`, as `python-calamine` and `xlsxwriter` are defined as the default engine via hard-coded statements in `/<package>/__init__.py`.

### Guidelines for Literal Strings

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

## Project-Specific Testing Instructions

### Test Data and Cache Management

- Any example data for tests should be included in a `tests/data` folder.
- When running tests, ensure that the cache path is used correctly: `./tests/test-cache`

### Test Fixtures and Data

- `cache_path` - Custom fixture providing a dedicated cache directory for tests
  - Defaults to `./tests/test-cache`
  - Ensures tests do not interfere with each other's cache data
  - Manual cleanup via `pytest --cache-clear` flag or test setup

## Guidelines for Backward Compatibility

- When changing code in a library or general function, if a change to an API or library
  will break backward compatibility, MENTION THIS to the user.
- DO NOT implement additional code for backward compatibility (such as extra methods or
  variable aliases or comments about backward compatibility) UNLESS the user has
  confirmed that it is necessary.