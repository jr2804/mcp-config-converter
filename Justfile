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
    uv run ruff check .
    uv run ruff format --check
    uv run isort --check-only .
    uv run undersort --check .

# Lint the documentation
lint-md:
    markdownlint -d -f "./**/*.md"

# Format the codebase
format:
    uv run ruff format .
    uv run ruff check --fix .
    uv run isort .
    uv run undersort --modify .

# Build the project
build:
    uv build .

# LLM overview
check-llm:
    @uv run -m mcp_config_converter llm-check