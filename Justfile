set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Default command - list all available commands
default:
	@just --list

# Clean generated artefacts
clean:
    uv run ruff clean
    uv run python scripts/clean.py

# Lint the codebase
lint:
    uv run ruff format --check
    uv run ruff check --fix tests mcp_config_converter
    uv run isort --check-only tests mcp_config_converter
    uv run undersort --check tests mcp_config_converter
    uv run ty check

# Lint the documentation
lint-md:
    uv run mdformat .\mcp_config_converter
    uv run mdformat docs
    uv run mdformat AGENTS.md README.md

# Format the codebase
format:
    uv run ruff format tests mcp_config_converter
    uv run isort tests mcp_config_converter
    uv run undersort tests mcp_config_converter

# Build the project
build:
    @uv run scripts/remove_version.py
    uv build --clear --refresh .

# Run tests
test:
    @cls
    @uv run pytest --cov=mcp_config_converter --cov-report=term-missing tests --tb=short

# LLM overview
check-llm:
    @cls
    @uv run -m mcp_config_converter llm-check

# Convert MCP config from .vscode/mcp.json to target format
# Args:
#   target: Target format (opencode, gemini, claude, vscode, etc.)
#   ...: Additional LLM provider arguments (e.g., --llm-provider ollama --llm-model -1)
convert target="opencode" *args:
    @cls
    @uv run -m mcp_config_converter convert .vscode/mcp.json --provider {{target}} {{args}}