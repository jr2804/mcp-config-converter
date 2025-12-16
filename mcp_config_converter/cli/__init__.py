"""CLI package exposing commands and app."""

import typer
from rich.console import Console

from mcp_config_converter import __version__

app = typer.Typer(
    name="mcp-config-converter",
    help="MCP Config Converter - Convert MCP configurations between formats and LLM providers with automatic provider selection.",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console = Console()
        console.print(f"mcp-config-converter v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """MCP Config Converter CLI."""
    pass


console = Console()

# Import all command modules to register commands - must happen after app creation
from mcp_config_converter.cli import convert, init, llm_check, validate  # noqa: E402, F401

__all__ = ["app"]
