# AGENTS.md - Guidelines for Coding Agents

## Project Overview

The MCP Config Converter is a Python-based tool designed to convert Model Context Protocol (MCP) configurations between different formats and providers. The project aims to address the fragmented ecosystem of MCP configurations across various LLM providers and development environments.

### Key Components

- **Parsers**: Handle input formats (JSON, YAML, TOML)
- **Formatters**: Generate provider-specific output (Claude, Gemini, VS Code, OpenCode)
- **LLM Providers**: AI-assisted conversion with multiple providers (OpenAI, Ollama, DeepSeek, SambaNova, Perplexity, OpenRouter)
- **Models**: Pydantic models for MCP configuration validation
- **CLI**: Command-line interface built with Typer and Rich

## Development Guidelines

### Code Style

- Follow Python best practices and PEP 8 guidelines
- Use type hints consistently
- Maintain consistent code formatting using the project's configured tools
- Keep functions focused and single-purpose

### Testing

- Write comprehensive tests for new features
- Ensure existing tests continue to pass
- Test edge cases and error conditions
- Use the existing test structure in the `tests/` directory

### Documentation

- Update README.md for significant changes
- Add docstrings to new functions and classes
- Keep documentation concise and focused

### Version Control

- Use meaningful commit messages
- Follow the existing commit message style
- Keep commits focused on specific changes

### Dependencies

- Use existing project dependencies when possible
- Add new dependencies only when necessary
- Update pyproject.toml for new dependencies

## Common Tasks

### Adding a New Parser

1. Create a new parser file in `parsers/` directory
2. Implement the `BaseParser` interface
3. Add tests in `tests/test_parsers.py`
4. Update the CLI to support the new format

### Adding a New Formatter

1. Create a new formatter file in `formatters/` directory
2. Implement the `BaseFormatter` interface
3. Add tests in `tests/test_formatters.py`
4. Update the CLI to support the new provider

### Adding a New LLM Provider

1. Create a new provider file in `llm/` directory
2. Implement the `BaseLLMProvider` interface or extend an existing provider (e.g., `OpenAIProvider` for OpenAI-compatible APIs)
3. For providers with multiple SDK options, create separate classes (e.g., `ProviderOpenAIProvider` and `ProviderSDKProvider`)
4. Add tests for the new provider
5. Update `llm/__init__.py` to export the new provider class
6. Make SDK dependencies optional in `pyproject.toml`

### Available LLM Providers

The project supports the following LLM providers for AI-assisted configuration conversion:

#### OpenAI-Compatible Providers:
- **OpenAI**: Standard OpenAI API with GPT models
- **DeepSeek**: DeepSeek API using OpenAI-compatible interface
- **SambaNovaOpenAI**: SambaNova API using OpenAI-compatible interface
- **PerplexityOpenAI**: Perplexity API using OpenAI-compatible interface

#### Proprietary SDK Providers:
- **SambaNovaSDK**: SambaNova API using proprietary SDK
- **PerplexitySDK**: Perplexity API using proprietary SDK
- **OpenRouter**: OpenRouter API using proprietary SDK

#### Local/Other Providers:
- **Ollama**: Local Ollama models
- **ClaudeProvider**: Anthropic Claude API (if implemented)
- **GeminiProvider**: Google Gemini API (if implemented)

#### Provider Configuration:
- Each provider supports API key via environment variable (e.g., `DEEPSEEK_API_KEY`, `PERPLEXITY_API_KEY`)
- Default models are configured for each provider
- Users can override models via `--model` CLI parameter
- OpenAI-compatible providers require `base_url` parameter where applicable

### Running Tests

```bash
pytest tests/
```

### Running Linters

```bash
ruff check
```

### Building the Project

```bash
pip install -e .
```

## Project Structure

```
mcp-config-converter/
├── mcp_config_converter/
│   ├── cli.py              # Command-line interface
│   ├── models.py           # Pydantic models for MCP configs
│   ├── transformers.py     # Configuration transformation logic
│   ├── parsers/            # Format-specific parsers
│   ├── formatters/         # Provider-specific formatters
│   └── utils.py            # Utility functions
└── tests/                  # Test suite
```

## Important Files

- `pyproject.toml`: Project configuration and dependencies
- `README.md`: Main project documentation
- `cli.py`: Entry point for the command-line interface
- `models.py`: Core data models for MCP configurations

## Best Practices

1. **Error Handling**: Implement proper error handling for file operations and data validation
2. **Logging**: Use appropriate logging for debugging and user feedback
3. **Performance**: Consider performance implications for large configuration files
4. **Security**: Never expose sensitive information in logs or error messages
5. **Compatibility**: Ensure backward compatibility when making changes

## Getting Help

For questions about the project or specific implementation details, refer to:
- The README.md file for general information
- Existing code in the relevant modules
- Test files for usage examples
- Project documentation in the docs/ directory (if available)
