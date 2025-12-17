from __future__ import annotations

import typer

from mcp_config_converter.cli import app
from mcp_config_converter.cli.arguments import version_callback


@app.command(name="version")
def version(
    ctx: typer.Context,
) -> None:
    """Show version and exit."""
    version_callback(True)
