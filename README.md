# MCP Config Converter

A configuration converter for the Model Context Protocol (MCP) with an enhanced CLI experience.

## Background

The Model Context Protocol (MCP) is a standardized protocol for communication between LLM applications and external context providers.
As MCP adoption grows across different LLM providers and development environments, each platform has developed its own configuration format and conventions for
defining MCP servers.

## Motivation

This project was created to address the challenges developers face when working with MCP configurations across multiple platforms:

### The Problem

- **Fragmented Ecosystem**: Different LLM providers (Claude, Gemini, etc.)
  and development environments (VS Code, OpenCode) use different configuration formats for MCP servers

- **Manual Conversion**: Developers often need to manually rewrite configurations when switching between platforms or sharing MCP server setups

- **Configuration Complexity**: MCP server configurations can include commands, arguments, environment variables, and metadata that need to be carefully
  preserved during conversion

- **Lack of Standardization**: While MCP itself is standardized, the configuration formats are not, leading to compatibility issues

### The Solution

`mcp-config-converter` provides a unified tool to:

1. **Parse Multiple Formats**: Read MCP configurations from JSON, YAML, and TOML files

1. **Convert Between Providers**: Transform configurations between different LLM provider formats (Claude, Gemini, VS Code, OpenCode)

1. **Preserve Semantics**: Maintain all configuration details including commands, arguments, environment variables, and metadata

1. **Validate Configurations**: Ensure MCP configurations are well-formed and complete

1. **Streamline Workflows**: Enable easy sharing and reuse of MCP server configurations across different platforms

## Key Features

- 🔄 **Multi-format Support**: Parse and generate JSON, YAML, and TOML configurations

- 🎯 **Provider-specific Formatting**: Output configurations optimized for Claude, Gemini, VS Code, OpenCode, and AI-assisted conversion with multiple LLM
  providers (OpenAI, Ollama, DeepSeek, SambaNova, Perplexity, OpenRouter)

- ✅ **Validation**: Validate MCP configurations against the protocol schema

- 🎨 **Rich CLI Experience**: User-friendly command-line interface with colorful output powered by Rich and Typer

- 🔧 **Extensible Architecture**: Easy to add support for new formats and providers

- 🤖 **Unified LLM Support**: Built on [LiteLLM](https://github.com/BerriAI/litellm), providing access to 100+ LLM providers through a single unified interface with automatic retry logic and exponential backoff

## LLM Provider Support

This project uses **LiteLLM** as a unified interface to support 100+ LLM providers. The LiteLLM integration provides:

- **Single Unified API**: One consistent interface for all LLM providers
- **Automatic Retry Logic**: Built-in retry mechanism with exponential backoff for rate limits and service unavailability
- **Smart Model Mapping**: Friendly model names automatically mapped to provider-specific identifiers
- **Flexible Configuration**: Support for API keys via environment variables or direct parameters

### Supported Providers & Models

The tool supports all major LLM providers through LiteLLM:

| Provider | Example Models | Environment Variable |
|----------|----------------|---------------------|
| **OpenAI** | `gpt-4`, `gpt-4o`, `gpt-3.5-turbo` | `OPENAI_API_KEY` |
| **Anthropic (Claude)** | `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229` | `ANTHROPIC_API_KEY` |
| **Google Gemini** | `gemini-2.5-flash`, `gemini-1.5-pro` | `GOOGLE_API_KEY`, `GEMINI_API_KEY` |
| **Ollama** | `ollama/llama2`, `ollama/mistral` | None (local) |
| **Mistral** | `mistral-large`, `mistral-medium` | `MISTRAL_API_KEY` |
| **DeepSeek** | `deepseek-chat`, `deepseek-coder` | `DEEPSEEK_API_KEY` |
| **Perplexity** | `sonar`, `sonar-pro` | `PERPLEXITY_API_KEY` |
| **OpenRouter** | `openai/gpt-4` | `OPENROUTER_API_KEY` |
| **SambaNova** | Various models | `SAMBANOVA_API_KEY` |

### Using LiteLLM Provider

The LiteLLM provider is automatically available and selected with the lowest cost priority:

```bash
# Use LiteLLM with automatic provider selection
uv run mcp-config-converter convert config.yaml --preferred-provider litellm --output output.json

# Use LiteLLM with a specific model
uv run mcp-config-converter convert config.yaml --preferred-provider litellm --llm-model gpt-4 --output output.json

# Use LiteLLM with Claude
uv run mcp-config-converter convert config.yaml --preferred-provider litellm --llm-model claude-3-5-sonnet-20241022 --output output.json

# Use LiteLLM with Ollama (no API key needed)
uv run mcp-config-converter convert config.yaml --preferred-provider litellm --llm-model ollama/llama2 --output output.json
```

## Installation

This project uses `uv` for dependency management. Install dependencies with:

```bash
uv sync
```

**Note**: With the unified LiteLLM implementation, all LLM providers are now supported out of the box without additional optional dependencies. Simply set the appropriate API key environment variable for your chosen provider.

### Environment Configuration

The tool supports loading API keys and configuration from a `.env` file. This allows you to securely manage your LLM provider credentials without hardcoding them.

1. **Copy the example file**:
```bash
cp .env.example .env
```

2. **Edit the `.env` file** and add your API keys:
```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic (Claude) API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Gemini API Key
GOOGLE_API_KEY=your_google_api_key_here

# Other providers...
```

3. **The `.env` file is automatically loaded** when running tests or the CLI tool, so you don't need to manually set environment variables.

**Note**: Never commit your `.env` file with real API keys! It's already excluded in `.gitignore`.

## Quick Start

```bash
# Convert an MCP configuration file to Claude format using LiteLLM with Ollama (local, no API key)
uv run mcp-config-converter convert config.yaml --provider claude --output claude_config.json --preferred-provider litellm --llm-model ollama/llama2

# Convert using LiteLLM with GPT-4
uv run mcp-config-converter convert config.yaml --provider claude --output output.json --preferred-provider litellm --llm-model gpt-4

# Convert using LiteLLM with Claude (requires ANTHROPIC_API_KEY)
uv run mcp-config-converter convert config.yaml --provider vscode --output output.json --preferred-provider litellm --llm-model claude-3-5-sonnet-20241022

# Use auto provider selection (picks best available provider)
uv run mcp-config-converter convert config.yaml --provider claude --output output.json --preferred-provider auto

# Check LLM provider status
uv run mcp-config-converter llm-check
```

## Use Cases

- **Cross-platform Development**: Develop MCP servers that work across multiple LLM platforms

- **Configuration Sharing**: Share MCP server setups with teams using different tools

- **Migration**: Move MCP configurations when switching between LLM providers

- **Standardization**: Maintain a single source of truth for MCP configurations in your preferred format

## Project Structure

```
mcp-config-converter/
├── mcp_config_converter/
│   ├── cli/                # Command-line interface modules
│   │   ├── arguments.py    # CLI argument parsing
│   │   ├── convert.py     # Convert command implementation
│   │   ├── llm_check.py   # LLM provider checking
│   │   ├── validate.py     # Validation command implementation
│   │   └── ...            # Other CLI modules
│   ├── llm/               # LLM provider implementations
│   │   ├── base.py        # Base LLM interface
│   │   ├── claude.py      # Claude provider
│   │   ├── deepseek.py    # DeepSeek provider
│   │   └── ...            # Other LLM providers
│   ├── prompts/           # LLM prompt templates
│   ├── specs/             # MCP provider specifications
│   ├── transformers.py     # Configuration transformation logic
│   ├── types.py           # Type definitions
│   └── utils.py           # Utility functions
└── tests/                 # Test suite
```

## Contributing

Contributions are welcome!
This project aims to support the growing MCP ecosystem by making configurations portable and accessible across platforms.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

This project supports the Model Context Protocol ecosystem and aims to improve interoperability between different MCP implementations.
