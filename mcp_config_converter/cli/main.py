from __future__ import annotations

from mcp_config_converter import __version__
from mcp_config_converter.cli import app, console


@app.command(name="version")
def version() -> None:
    """Show version and exit."""
    console.print(f"MCP Config Converter v{__version__}")
