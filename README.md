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

## Installation

```bash
pip install mcp-config-converter
```

### Optional Dependencies

For specific LLM providers, install with optional dependencies:

```bash
# Install with Anthropic Claude support
pip install mcp-config-converter[anthropic]

# Install with SambaNova support
pip install mcp-config-converter[sambanova]

# Install with Perplexity support
pip install mcp-config-converter[perplexity]

# Install with OpenRouter support
pip install mcp-config-converter[openrouter]

# Install with Ollama support
pip install mcp-config-converter[ollama]

# Install with all optional dependencies
pip install mcp-config-converter[all]
```

## Quick Start

```bash
# Convert an arbitrary MCP server configuration file `config.yaml` to Claude format via Ollama LLM provider
mcp-config-converter convert config.yaml --provider claude -o claude_config.json --preferred-provider ollama

# Convert configuration using custom LLM provider with Anthropic-compatible API
mcp-config-converter convert config.yaml --llm-provider-type anthropic --llm-api-key YOUR_API_KEY --llm-base-url https://api.anthropic.com/v1 --llm-model claude-2

# Convert configuration using custom LLM provider with OpenAI-compatible API
mcp-config-converter convert config.yaml --llm-provider-type openai --llm-api-key YOUR_API_KEY --llm-base-url https://api.example.com/v1 --llm-model custom-model

# Validate an MCP configuration
mcp-config-converter validate config.json
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
│   ├── cli.py              # Command-line interface
│   ├── models.py           # Pydantic models for MCP configs
│   ├── transformers.py     # Configuration transformation logic
│   ├── parsers/            # Format-specific parsers (JSON, YAML, TOML)
│   ├── formatters/         # Provider-specific formatters
│   └── utils.py            # Utility functions
└── tests/                  # Test suite
```

## Contributing

Contributions are welcome!
This project aims to support the growing MCP ecosystem by making configurations portable and accessible across platforms.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

This project supports the Model Context Protocol ecosystem and aims to improve interoperability between different MCP implementations.
