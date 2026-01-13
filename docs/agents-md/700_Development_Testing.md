# Test-driven Development and Best Practices

## Instructions on Testing

- Use `pytest` for writing and running tests.
- After adding new or updating existing features, include pytest-based unit tests/test functions.
- Aim for high test coverage to ensure code reliability and facilitate future changes.
- Regularly run tests to catch issues early and ensure code quality.
- Refactor tests as needed to keep them maintainable and aligned with code changes.
- Use fixtures and parameterized tests to reduce code duplication and improve test coverage.
- Leverage mocking and patching to isolate tests and avoid dependencies on external systems.
- Any example data for tests should be included in a `tests/data` folder.
- When running tests, ensure that the cache path is used correctly: `./tests/test-cache`
- When writing tests, follow the Arrange-Act-Assert (AAA) pattern for clarity and maintainability.

For CI/Full Test Runs:

```bash
# Full test suite including conformance tests
uv run pytest -v

```

### Test Fixtures and Data

- `tmp_path` - Pytest built-in fixture providing temporary directory
  - Automatically cleaned up after test
  - Use for tests that need to write files
- `monkeypatch` - Pytest built-in fixture for modifying environment variables or attributes
  - Use to mock external dependencies or configurations
- `cache_path` - Custom fixture providing a dedicated cache directory for tests
  - Defaults to `./tests/test-cache`
  - Ensures tests do not interfere with each other's cache data
  - Manual cleanup via `pytest --cache-clear` flag or test setup

## Testing Strategy

- Test all public methods and edge cases.
- Use parametrized tests for different input scenarios.
- Mock external dependencies appropriately.
- Achieve >95% line coverage for non-generated application code (excluding configuration files, migrations, vendored dependencies, and auto-generated code) as reported by the project's coverage tooling.
- Include property-based testing with Hypothesis.
