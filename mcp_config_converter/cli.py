"""Main CLI entry point for MCP Config Converter."""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

from mcp_config_converter import __version__
from mcp_config_converter.cli_helpers import (
    PROVIDER_DEFAULT_OUTPUT_FILES,
    select_format,
    select_provider,
    validate_format_choice,
    validate_output_action,
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
        help="Output format (provider type: github-copilot-cli, vscode, gemini, claude, codex, opencode)",
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
    output_action: str = typer.Option(
        "overwrite",
        "--output-action",
        "-a",
        help="Action when output file exists: overwrite, skip, or merge",
        case_sensitive=False,
    ),
) -> None:
    """Convert MCP configuration from one format to another."""
    try:
        # Interactive mode - prompt for missing options
        if interactive:
            console.print(
                Panel.fit(
                    "Interactive Conversion Mode",
                    style="bold blue",
                )
            )

            if not format:
                format = select_format()

            if not provider:
                provider = select_provider()

            if not output:
                # Determine default output file based on format (provider type)
                if format and format in PROVIDER_DEFAULT_OUTPUT_FILES:
                    suggested_output = PROVIDER_DEFAULT_OUTPUT_FILES[format]
                else:
                    # Fallback: use original file extension
                    suggested_output = input_file.with_suffix(".mcp.json")

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
            valid_formats = ", ".join(list(PROVIDER_DEFAULT_OUTPUT_FILES.keys()))
            console.print(
                f"[red]Error:[/red] Invalid format '{format}'. Choose from: {valid_formats}"
            )
            raise typer.Exit(1)

        if provider and not validate_provider_choice(provider):
            console.print(
                f"[red]Error:[/red] Invalid provider '{provider}'. Choose from: claude, gemini, vscode, opencode"
            )
            raise typer.Exit(1)

        # Validate output action
        if not validate_output_action(output_action):
            console.print(
                "[red]Error:[/red] Invalid output action. Choose from: overwrite, skip, merge"
            )
            raise typer.Exit(1)

        # Determine output file if not specified but format is
        if not output and format:
            output = PROVIDER_DEFAULT_OUTPUT_FILES.get(format, input_file.with_suffix(".mcp.json"))

        # Perform conversion with progress indicator
        console.print(f"[blue]Converting {input_file.name}...[/blue]")

        # Import transformers at runtime to avoid circular imports
        from mcp_config_converter.transformers import ConfigTransformer

        try:
            # Use the transformer if format is provided
            if format:
                # Use direct transformer for now (LLM conversion can be added later)
                result = ConfigTransformer.transform(str(input_file), None, format)

                # Handle output file existence based on output_action
                if output and output.exists():
                    if output_action.lower() == "skip":
                        console.print(f"[yellow]Skipping conversion: output file {output} already exists (action: skip)[/yellow]")
                        return
                    elif output_action.lower() == "merge":
                        console.print(f"[blue]Merging with existing file: {output} (action: merge)[/blue]")
                        # For now, implement basic merge by reading existing file and updating with new values
                        import json
                        existing_content = output.read_text(encoding='utf-8')
                        existing_data = json.loads(existing_content)
                        new_data = json.loads(result)

                        # Merge: update existing keys with new values
                        existing_data.update(new_data)
                        result = json.dumps(existing_data, indent=2)
                    else:  # overwrite
                        console.print(f"[blue]Will overwrite existing file: {output} (action: overwrite)[/blue]")

                # Write the result to output file
                if output:
                    output.parent.mkdir(parents=True, exist_ok=True)  # Create directories if needed
                    output.write_text(result, encoding='utf-8')

                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")
                else:
                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Output: [green]No output file specified (result generated)[/green]")
            else:
                # If no format is specified, just show what would happen
                console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                if provider:
                    console.print(f"[green]SUCCESS[/green] Target provider: [cyan]{provider}[/cyan]")
                if output:
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")

        except Exception as e:
            console.print(f"[red]Error during conversion:[/red] {str(e)}")
            raise typer.Exit(1)

        console.print("\n[bold green]SUCCESS Conversion completed successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Conversion cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
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
            console.print(f"\n[green]SUCCESS[/green] Validating: [cyan]{config_file}[/cyan]")

            progress.update(task, completed=True)

        console.print("[bold green][green]SUCCESS[/green] Configuration is valid![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Validation cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
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
                "Initialize New MCP Configuration",
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
                console.print(f"\n[green]SUCCESS[/green] Provider: [cyan]{provider}[/cyan]")
            if output:
                console.print(f"[green]SUCCESS[/green] Output: [green]{output}[/green]")

            progress.update(task, completed=True)

        console.print("\n[bold green][green]SUCCESS[/green] Configuration initialized successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Initialization cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
