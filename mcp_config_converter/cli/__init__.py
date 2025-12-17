"""CLI package exposing commands and app."""

import typer
from rich.console import Console

app = typer.Typer(
    name="mcp-config-converter",
    help="MCP Config Converter - Convert MCP configurations between formats and LLM providers with automatic provider selection.",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

console = Console()


# Import all command modules to register commands - must happen after app creation
from mcp_config_converter.cli import convert, llm_check, validate, ver  # noqa: E402, F401

__all__ = ["app"]
