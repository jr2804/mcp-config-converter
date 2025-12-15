from __future__ import annotations

import typer
from rich.console import Console

from mcp_config_converter import __version__
from mcp_config_converter.cli import arguments, convert, init, llm_check, validate

console = Console()

app = typer.Typer(
    name="mcp-config-converter",
    help="MCP Config Converter - Convert MCP configurations between formats and LLM providers with automatic provider selection.",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    if value:
        console.print(f"MCP Config Converter v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    llm_base_url: str | None = arguments.llm_base_url_option(),
    llm_provider_type: str | None = arguments.llm_provider_type_option(),
    llm_api_key: str | None = arguments.llm_api_key_option(),
    llm_model: str | None = arguments.llm_model_option(),
    preferred_provider: str = arguments.preferred_provider_option(),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
) -> None:
    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["llm_config"] = {
        "base_url": llm_base_url,
        "provider_type": llm_provider_type,
        "api_key": llm_api_key,
        "model": llm_model,
    }
    ctx.obj["preferred_provider"] = preferred_provider
    ctx.obj["verbose"] = verbose


typer.run = app

app.command()(convert.convert)
app.command()(validate.validate)
app.command()(init.init)
app.command()(llm_check.llm_check)
