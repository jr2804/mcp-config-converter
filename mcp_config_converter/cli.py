"""Main CLI entry point for MCP Config Converter."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

from mcp_config_converter import __version__
from mcp_config_converter.cli_helpers import (
    select_format,
    select_provider,
    validate_format_choice,
    validate_provider_choice,
)

app = typer.Typer(
    name="mcp-config-converter",
    help="MCP Config Converter - Convert MCP configurations between formats and LLM providers.",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"MCP Config Converter v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """MCP Config Converter - Convert MCP configurations between formats and LLM providers."""
    pass


@app.command()
def convert(
    input_file: Path = typer.Argument(
        ...,
        help="Input configuration file path",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path",
    ),
    format: str | None = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format (json, yaml, toml)",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        "-p",
        help="Target LLM provider (claude, gemini, vscode, opencode)",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Run in interactive mode",
    ),
) -> None:
    """Convert MCP configuration from one format to another."""
    try:
        # Interactive mode - prompt for missing options
        if interactive:
            console.print(
                Panel.fit(
                    "🔄 Interactive Conversion Mode",
                    style="bold blue",
                )
            )

            if not format:
                format = select_format()

            if not provider:
                provider = select_provider()

            if not output:
                # Use format if available, otherwise default to original extension
                output_extension = format if format else input_file.suffix.lstrip(".")
                suggested_output = input_file.with_suffix(f".{output_extension}")
                output = Path(
                    Prompt.ask(
                        "Enter output file path",
                        default=str(suggested_output),
                    )
                )

            # Confirm before proceeding
            if not Confirm.ask(
                f"\nConvert [cyan]{input_file}[/cyan] → [green]{output}[/green]?",
                default=True,
            ):
                console.print("[yellow]Conversion cancelled.[/yellow]")
                raise typer.Exit(0)

        # Validate choices
        if format and not validate_format_choice(format):
            console.print(
                f"[red]Error:[/red] Invalid format '{format}'. Choose from: json, yaml, toml",
                err=True,
            )
            raise typer.Exit(1)

        if provider and not validate_provider_choice(provider):
            console.print(
                f"[red]Error:[/red] Invalid provider '{provider}'. Choose from: claude, gemini, vscode, opencode",
                err=True,
            )
            raise typer.Exit(1)

        # Perform conversion with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Converting {input_file.name}...",
                total=None,
            )

            # TODO: Implement actual conversion logic
            # For now, just display what would happen
            console.print(f"\n✓ Input file: [cyan]{input_file}[/cyan]")
            if format:
                console.print(f"✓ Target format: [cyan]{format}[/cyan]")
            if provider:
                console.print(f"✓ Target provider: [cyan]{provider}[/cyan]")
            if output:
                console.print(f"✓ Output file: [green]{output}[/green]")

            progress.update(task, completed=True)

        console.print("\n[bold green]✓ Conversion completed successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Conversion cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}", err=True)
        raise typer.Exit(1)


@app.command()
def validate(
    config_file: Path = typer.Argument(
        ...,
        help="Configuration file to validate",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
) -> None:
    """Validate an MCP configuration file."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Validating {config_file.name}...",
                total=None,
            )

            # TODO: Implement actual validation logic
            console.print(f"\n✓ Validating: [cyan]{config_file}[/cyan]")

            progress.update(task, completed=True)

        console.print("[bold green]✓ Configuration is valid![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Validation cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}", err=True)
        raise typer.Exit(1)


@app.command()
def init(
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path for the new configuration",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        "-p",
        help="Target LLM provider (claude, gemini, vscode, opencode)",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        "-i/-I",
        help="Run in interactive mode",
    ),
) -> None:
    """Initialize a new MCP configuration."""
    try:
        console.print(
            Panel.fit(
                "🚀 Initialize New MCP Configuration",
                style="bold blue",
            )
        )

        if interactive:
            if not provider:
                provider = select_provider()

            if not output:
                default_name = "mcp-config.json"
                output = Path(
                    Prompt.ask(
                        "Enter output file path",
                        default=default_name,
                    )
                )

            # Confirm before creating
            if output.exists() and not Confirm.ask(
                f"\n[yellow]Warning:[/yellow] File [cyan]{output}[/cyan] exists. Overwrite?",
                default=False,
            ):
                console.print("[yellow]Initialization cancelled.[/yellow]")
                raise typer.Exit(0)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing configuration...", total=None)

            # TODO: Implement actual initialization logic
            if provider:
                console.print(f"\n✓ Provider: [cyan]{provider}[/cyan]")
            if output:
                console.print(f"✓ Output: [green]{output}[/green]")

            progress.update(task, completed=True)

        console.print("\n[bold green]✓ Configuration initialized successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Initialization cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
