from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

from mcp_config_converter.cli import app, arguments
from mcp_config_converter.cli.utils import CliPrompt, configure_llm_provider, console


@app.command(name="init")
def init(
    ctx: typer.Context,
    output: Path | None = arguments.OutputOpt,
    provider: str | None = arguments.InitProviderOpt,
    interactive: bool = arguments.InteractiveOpt,
    llm_base_url: str | None = arguments.LlmBaseUrlOpt,
    llm_provider_type: str | None = arguments.LlmProviderTypeOpt,
    llm_api_key: str | None = arguments.LlmApiKeyOpt,
    llm_model: str | None = arguments.LlmModelOpt,
    preferred_provider: str = arguments.PreferredProviderOpt,
    verbose: bool = arguments.VerboseOpt,
) -> None:
    """Initialize a new MCP configuration."""
    try:
        configure_llm_provider(ctx, verbose=verbose)

        if sys.platform == "win32":
            console.print("\n[bold blue]Initialize New MCP Configuration[/bold blue]")
        else:
            console.print(
                Panel.fit(
                    "Initialize New MCP Configuration",
                    style="bold blue",
                )
            )

        if interactive:
            if not provider:
                provider = CliPrompt.select_provider()

            if not output:
                default_name = "mcp-config.json"
                output = Path(Prompt.ask("Enter output file path", default=default_name))

            if output.exists() and not Confirm.ask(
                f"\n[yellow]Warning:[/yellow] File [cyan]{output}[/cyan] exists. Overwrite?",
                default=False,
            ):
                console.print("[yellow]Initialization cancelled.[/yellow]")
                raise typer.Exit(0)

        def run_initialization(progress: Progress) -> None:
            task = progress.add_task("Initializing configuration...", total=None)

            if provider:
                console.print(f"\n[green]SUCCESS[/green] Provider: [cyan]{provider}[/cyan]")
            if output:
                console.print(f"[green]SUCCESS[/green] Output: [green]{output}[/green]")

            progress.update(task, completed=True)

        if sys.platform == "win32":
            with Progress(TextColumn("[progress.description]{task.description}"), console=console) as progress:
                run_initialization(progress)
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                run_initialization(progress)

        console.print("\n[bold green]Configuration initialized successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Initialization cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as exc:
        console.print(f"\n[red]Error:[/red] {str(exc)}")
        raise typer.Exit(1)
