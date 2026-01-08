# Project-Specific Testing Configuration

> **Note:** For universal testing patterns, pytest usage, and best practices, refer to the skills in `.claude/skills/development/`:
>
> - [testing_strategy](../../.claude/skills/development/testing_strategy/SKILL.md) - Testing patterns, coverage, fixtures
> - [python_guidelines](../../.claude/skills/development/python_guidelines/SKILL.md) - Python-specific testing guidance

## Project-Specific Rules

### Test Cache Location

When running tests, ensure that the cache path is used correctly: `./tests/test-cache`

### Test Data Location

Any example data for tests should be included in a `tests/data` folder.

### Coverage Target

Achieve >**95% line coverage** for non-generated application code (excluding configuration files, migrations, vendored dependencies, and auto-generated code) as reported by the project's coverage tooling.

Note: This is higher than the typical 90% target used in most projects.

### Test Pattern

When writing tests, follow the **Arrange-Act-Assert (AAA)** pattern for clarity and maintainability.

For CI/Full Test Runs:

```bash
# Full test suite including conformance tests
uv run pytest -v
```

