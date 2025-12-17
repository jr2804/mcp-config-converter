# Project Guidelines for Agentic Coding

This project must only be managed and run via "uv". Avoid direct usage of `python <script>` or `python -m <module>`.

## 1. Project Management with uv

### Installation and Execution

- To run the CLI: `uv run mcp-config-converter <command> [OPTIONS]`
- To run a Python script: `uv run script.py`
- To run a module: `uv run -m module_name`

### Dependency Management

Use `uv add` for managing dependencies. This ensures consistency with the project's uv-based dependency management and maintains proper lock file synchronization.

- To add a new dependency: `uv add <package-name>`
- To add a dependency with extras: `uv add <package-name>[extra1,extra2]`
- To add a dev dependency: `uv add --dev <package-name>`
- To install all dependencies from pyproject.toml: `uv sync`

## 2. LLM Providers and `llm-check` Command

### Preferred Provider Selection

The `--preferred-provider` option allows automatic selection of LLM providers:

- `auto` (default): Automatically selects the lowest-cost available provider from the registry.
- Specific provider name: Uses the specified provider if configured.

**Cost Hierarchy** (lowest to highest cost):
- Ollama: 1 (preferred local)
- DeepSeek: 8
- Perplexity: 10/11
- Gemini: 12
- OpenAI: 15
- SambaNova: 16/17
- OpenRouter: 18
- Claude: 20
- Mistral: 25

The system selects the first provider that:

1. Has required dependencies installed.
2. Has valid API keys configured (if required).
3. Can successfully create a client.

**Custom Providers**: Create custom LLM providers using `--llm-base-url` and `--llm-provider-type`. They get cost `-1` and are always preferred in auto-selection.

### Available Providers

The `llm-check` command automatically discovers and checks all registered providers:

- Claude (Anthropic)
- DeepSeek
- Gemini (Google)
- Mistral
- Ollama (Local)
- OpenAI
- OpenRouter
- Perplexity (OpenAI-compatible and SDK)
- SambaNova (OpenAI-compatible and SDK)

### `llm-check` Usage

The command provides a comprehensive status overview.

```bash
uv run mcp-config-converter llm-check [OPTIONS]
```

**Output Columns:** Provider, Model, Availability (Status OK/Failed), Authentication (Status OK/Failed/n/a), Cost (sorted by increasing cost).

### Optional Dependencies

SDK dependencies are optional and available as dependency groups in `pyproject.toml`. The project handles missing dependencies gracefully with clear error messages.

- `anthropic`: For Claude provider support.
- `sambanova`: For SambaNova SDK provider.
- `perplexity`: For Perplexity SDK provider.
- `openrouter`: For OpenRouter SDK provider.
- `ollama`: For Ollama provider.
- `all`: All optional dependencies.

**Installation Example (using uv):**

```bash
uv add mcp-config-converter[anthropic]    # Claude support
uv add mcp-config-converter[all]            # All dependencies
```

### Provider Registry

All providers register with `@ProviderRegistry.register_provider("name", cost=X)`. Custom providers can be created dynamically via `ProviderRegistry.create_provider()`.

## 3. Development Commands

Standard project commands, run via `uv run`:

- **Run single test**: `uv run pytest tests/test_cli.py::test_cli_help -v`
- **Run all tests**: `uv run just test`
- **Lint**: `uv run just lint`
- **Typecheck**: `uv run just typecheck`
- **Build**: `uv run just build`

## 4. Security Guidelines

- **Input Validation**: Always validate user inputs before processing to prevent security vulnerabilities.
- **Principle of Least Privilege**: Follow the principle of least privilege when dealing with permissions.
- **Dependency Management**: Keep dependencies up to date to avoid security vulnerabilities.
- **Configuration**: Use environment variables for configuration instead of hardcoding values.

## 5. Testing Guidelines

- **Write Tests**: Write tests for critical functionality to ensure code reliability.
- **Test Coverage**: Focus on testing complex algorithms and business logic.

## 6. Documentation Guidelines

- **Document Complex Logic**: Document complex algorithms and business logic for future maintainability.
- **Code Comments**: Use descriptive variable and function names for better code readability.
- **Avoid Premature Optimization**: Make it work first, then optimize if needed.

## 5. Code Style

- **Imports**: Use absolute imports, group by stdlib, third-party, local; sort alphabetically.
- **Formatting**: Ruff with `ruff.toml` (no line length limit, double quotes).
- **Types**: Add type hints to all functions/methods.
- **Naming**: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- **Error Handling**: Use the Result pattern, handle exceptions gracefully, provide meaningful error messages.
