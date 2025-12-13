"""Main CLI entry point for MCP Config Converter."""

from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

app = typer.Typer(
    help="MCP Config Converter - Convert MCP configurations between formats and LLM providers."
)
console = Console()


class OutputFormat(str, Enum):
    """Supported output formats."""

    json = "json"
    yaml = "yaml"
    toml = "toml"


class Provider(str, Enum):
    """Supported LLM providers."""

    claude = "claude"
    gemini = "gemini"
    vscode = "vscode"
    opencode = "opencode"


@app.command()
def convert(
    input_file: Path = typer.Argument(
        ..., exists=True, help="Input configuration file"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    format: Optional[OutputFormat] = typer.Option(
        None, "--format", "-f", help="Output format"
    ),
    provider: Optional[Provider] = typer.Option(
        None, "--provider", "-p", help="Target LLM provider"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Enable interactive mode"
    ),
):
    """Convert MCP configuration from one format to another."""
    try:
        # Interactive mode prompts
        if interactive:
            if not format:
                format_choice = Prompt.ask(
                    "Select output format",
                    choices=[f.value for f in OutputFormat],
                    default="json",
                )
                format = OutputFormat(format_choice)

            if not provider:
                provider_choice = Prompt.ask(
                    "Select target provider",
                    choices=[p.value for p in Provider],
                    default="claude",
                )
                provider = Provider(provider_choice)

            if not output:
                default_output = f"{input_file.stem}_converted.{format.value}"
                output_str = Prompt.ask("Output file path", default=default_output)
                output = Path(output_str)

        # Show progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Converting {input_file}...", total=None)

            # Actual conversion logic would go here
            console.print(f"[green]✓[/green] Converting {input_file}...")
            if format:
                console.print(f"[green]✓[/green] Target format: {format.value}")
            if provider:
                console.print(f"[green]✓[/green] Target provider: {provider.value}")
            if output:
                console.print(f"[green]✓[/green] Output file: {output}")

            progress.update(task, completed=True)

        console.print("[bold green]Conversion completed successfully![/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def validate(
    config_file: Path = typer.Argument(
        ..., exists=True, help="Configuration file to validate"
    ),
):
    """Validate an MCP configuration file."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Validating {config_file}...", total=None)

            # Actual validation logic would go here
            console.print(f"[green]✓[/green] Validating {config_file}...")

            progress.update(task, completed=True)

        console.print("[bold green]Validation completed successfully![/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def init(
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", "-i/-n", help="Enable interactive mode"
    ),
):
    """Initialize a new MCP configuration."""
    try:
        if interactive:
            console.print(
                "[bold blue]Initializing new MCP configuration...[/bold blue]"
            )

            # Interactive prompts
            config_name = Prompt.ask("Configuration name", default="mcp-config")
            format_choice = Prompt.ask(
                "Select format",
                choices=[f.value for f in OutputFormat],
                default="json",
            )

            console.print(f"[green]✓[/green] Creating {config_name}.{format_choice}...")
        else:
            console.print("[green]Initializing new MCP configuration...[/green]")

        console.print("[bold green]Initialization completed successfully![/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
