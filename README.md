# MCP Config Converter

A configuration converter for MCP (Model Context Protocol) with enhanced CLI experience.

## Features

- Convert MCP configurations between different formats (JSON, YAML, TOML)
- Transform configurations for different LLM providers (Claude, Gemini, VS Code, OpenCode)
- Interactive mode with rich prompts for easy configuration
- Beautiful console output with Rich library
- Progress indicators for long-running operations

## Installation

```bash
pip install -e .
```

## Usage

### Convert a configuration file

```bash
# Basic conversion
mcp-config-converter convert input.json --format yaml --provider claude

# Interactive mode
mcp-config-converter convert input.json --interactive
```

### Validate a configuration

```bash
mcp-config-converter validate config.json
```

### Initialize a new configuration

```bash
# Interactive mode (default)
mcp-config-converter init

# Non-interactive mode
mcp-config-converter init --no-interactive
```

## Testing

Run tests with pytest:

```bash
pip install -e ".[dev]"
pytest
```

## Development

The CLI is built with:
- **Typer**: Modern CLI framework with type hints
- **Rich**: Beautiful terminal output and progress bars
- **Pydantic**: Data validation and settings management

## License

See LICENSE file for details.
