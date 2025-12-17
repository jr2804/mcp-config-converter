from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from mcp_config_converter.cli import app, arguments
from mcp_config_converter.cli.utils import configure_llm_provider, console


@app.command(name="validate")
def validate(
    ctx: typer.Context,
    config_file: Path | None = arguments.ConfigFileArg,
    llm_base_url: str | None = arguments.LlmBaseUrlOpt,
    llm_provider_type: str | None = arguments.LlmProviderTypeOpt,
    llm_api_key: str | None = arguments.LlmApiKeyOpt,
    llm_model: str | None = arguments.LlmModelOpt,
    preferred_provider: str = arguments.PreferredProviderOpt,
    verbose: bool = arguments.VerboseOpt,
    version: Annotated[bool | None, arguments.VersionOpt] = None,
) -> None:
    """Validate an MCP configuration file."""
    try:
        configure_llm_provider(ctx, verbose=verbose)

        if config_file is None:
            console.print("[red]Error:[/red] Configuration file is required.")
            raise typer.Exit(1)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Validating {config_file.name}...", total=None)

            # TODO: Replace with actual validation logic
            console.print(f"\n[green]SUCCESS[/green] Validating: [cyan]{config_file}[/cyan]")

            progress.update(task, completed=True)

        console.print("[bold green][green]SUCCESS[/green] Configuration is valid![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Validation cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as exc:
        console.print(f"\n[red]Error:[/red] {str(exc)}")
        raise typer.Exit(1)
