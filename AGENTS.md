# Agents and LLM Providers

## llm-check Command

The `llm-check` command provides a comprehensive overview of all available LLM providers and their status. It displays a tabular view showing provider information, availability, and authentication status.

### Usage

```bash
mcp-config-converter llm-check [OPTIONS]
```

### Options

- `--llm-base-url`: Base URL for custom OpenAI-compatible providers
- `--llm-provider-type`: Provider type for custom OpenAI-compatible providers
- `--llm-model`: Model name for custom OpenAI-compatible providers

### Output Format

The command displays a table with the following columns:

- Provider: Name of the LLM provider
- Model: Currently configured or default model
- Availability: Status of provider (green checkmark if OK, red cross if failed)
- Authentication: Status of authentication (green checkmark if OK, red cross if failed, yellow "n/a" if not applicable)

If `--llm-base-url`, `--llm-provider-type`, and `--llm-model` are all provided, a row for "Custom OpenAI-Provider" will be included.

### Preferred Provider Selection

The `--preferred-provider` option allows automatic selection of LLM providers:

- `auto` (default): Automatically selects the first fully configured provider from the registry
- Specific provider name: Uses the specified provider if configured

When using `auto` selection, the system checks each provider in registry order and selects the first one that:

1. Has required dependencies installed
2. Has valid API keys configured (if required)
3. Can successfully create a client

If no providers are configured, an error is displayed with instructions to configure at least one provider.

### Available Providers

The llm-check command automatically discovers and checks all registered providers:

- Claude (Anthropic)
- DeepSeek
- Gemini (Google)
- Mistral
- Ollama (Local)
- OpenAI
- OpenRouter
- Perplexity (OpenAI-compatible and SDK)
- SambaNova (OpenAI-compatible and SDK)

Custom providers can also be checked by specifying `--llm-provider-type`, `--llm-base-url`, and `--llm-model`.

## Project Management

This project must only be managed and run via "uv" ... no usage of "python <script>" or "python -m <module>". Always use "uv run <script.py>" or "uv run -m <module>".

### Installation and Execution

- To run the CLI: `uv run mcp-config-converter <command> [OPTIONS]`
- To run a Python script: `uv run script.py`
- To run a module: `uv run -m module_name`

### Dependency Management

Use "uv add" instead of "pip install" for managing project dependencies:

- To add a new dependency: `uv add <package-name>`
- To add a dependency with extras: `uv add <package-name>[extra1,extra2]`
- To add a dev dependency: `uv add --dev <package-name>`
- To install all dependencies from pyproject.toml: `uv sync`

This ensures consistency with the project's uv-based dependency management and maintains proper lock file synchronization.

## llm-check Command

The `llm-check` command provides a comprehensive overview of all available LLM providers and their status. It displays a tabular view showing provider information, availability, and authentication status.

### Usage

```bash
mcp-config-converter llm-check [OPTIONS]
```

### Options

- `--llm-base-url`: Base URL for custom OpenAI-compatible providers
- `--llm-provider-type`: Provider type for custom OpenAI-compatible providers
- `--llm-model`: Model name for custom OpenAI-compatible providers

### Output Format

The command displays a table with the following columns:

- Provider: Name of the LLM provider
- Model: Currently configured or default model
- Availability: Status of provider (green checkmark if OK, red cross if failed)
- Authentication: Status of authentication (green checkmark if OK, red cross if failed, yellow "n/a" if not applicable)

If `--llm-base-url`, `--llm-provider-type`, and `--llm-model` are all provided, a row for "Custom OpenAI-Provider" will be included.

### Dependencies

1. **OpenAI SDK**: Already available in project
2. **Optional Dependencies**: Available as dependency groups in `pyproject.toml`:
   - `anthropic`: For Claude provider support
   - `sambanova`: For SambaNova SDK provider
   - `perplexity`: For Perplexity SDK provider
   - `openrouter`: For OpenRouter SDK provider
   - `ollama`: For Ollama provider
   - `all`: All optional dependencies

### Dependency Management

1. **Optional Dependencies**: SDK dependencies are optional and can be installed via extras
2. **Installation Examples**:

   ```bash
   pip install mcp-config-converter[anthropic]    # Claude support
   pip install mcp-config-converter[sambanova]   # SambaNova support
   pip install mcp-config-converter[all]            # All dependencies
   ```

3. **Graceful Degradation**: Handle missing dependencies gracefully
4. **Import Error Handling**: Provide clear error messages
5. **Test Coverage**: Test both with and without dependencies
