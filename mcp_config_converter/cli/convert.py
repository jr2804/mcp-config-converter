from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from mcp_config_converter.cli.constants import PROVIDER_DEFAULT_OUTPUT_FILES, SUPPORTED_PROVIDERS
from mcp_config_converter.cli.utils import (
    CliPrompt,
    console,
    validate_format_choice,
    validate_output_action,
)
from mcp_config_converter.transformers import ConfigTransformer


def convert(
    ctx: typer.Context,
    input_file: Path | None = typer.Argument(None, help="Input configuration file path"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str | None = typer.Option(None, "--format", "-f", help="Target provider format (claude, gemini, vscode, opencode)"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Run in interactive mode"),
    output_action: str = typer.Option(
        "overwrite", "--output-action", "-a", help="Action when output file exists: overwrite, skip, or merge", case_sensitive=False
    ),
    preferred_provider: str = typer.Option(
        "auto", "--preferred-provider", "-pp", help="Preferred LLM provider ('auto' for automatic selection, or specific provider name)", case_sensitive=False
    ),
    input_content: str | None = typer.Option(None, "--input-content", "-c", help="Raw input configuration content (alternative to input file)"),
    encode_toon: bool = typer.Option(True, "--encode-toon/--no-encode-toon", help="Encode JSON input to TOON format for LLM processing"),
    decode_toon: bool = typer.Option(True, "--decode-toon/--no-decode-toon", help="Decode TOON output from LLM back to JSON format"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
) -> None:
    """Convert an MCP configuration file to a supported format using LLM.

    Args:
        ctx: Typer context
        input_file: Input file path
        output: Output file path
        format: Target provider format (claude, gemini, vscode, opencode)
        interactive: Run in interactive mode
        output_action: Action when output file exists
        preferred_provider: Preferred LLM provider for conversion
        input_content: Raw input configuration content
        encode_toon: Whether to encode JSON input to TOON format
        decode_toon: Whether to decode TOON output back to JSON
        verbose: Verbose output
    """
    try:
        # Validate input source
        if input_file is None and input_content is None:
            console.print("[red]Error: Either input file or --input-content must be provided[/red]")
            raise typer.Exit(1)

        # Handle input source (file or content)
        if input_content is not None:
            # Using raw content input
            actual_input_file = None
        else:
            # Using file input
            actual_input_file = input_file
            input_content = None

        if interactive:
            console.print(Panel.fit("Interactive Conversion Mode", style="bold blue"))

            if not format:
                format = CliPrompt.select_format()

            if not output:
                suggested_output = PROVIDER_DEFAULT_OUTPUT_FILES.get(format)
                output = Path(Prompt.ask("Enter output file path", default=str(suggested_output)))

            if not Confirm.ask(
                f"\nConvert [cyan]{input_file}[/cyan] → [green]{output}[/green]",
                default=True,
            ):
                console.print("[yellow]Conversion cancelled.[/yellow]")
                raise typer.Exit(0)

        if format and not validate_format_choice(format):
            valid_formats = ", ".join(SUPPORTED_PROVIDERS)
            console.print(f"[red]Error:[/red] Invalid format '{format}'. Choose from: {valid_formats}")
            raise typer.Exit(1)

        if not validate_output_action(output_action):
            console.print("[red]Error:[/red] Invalid output action. Choose from: overwrite, skip, merge")
            raise typer.Exit(1)

        if not output and format:
            default_suffix = input_file.with_suffix(".mcp.json") if input_file else Path("input.mcp.json")
            output = PROVIDER_DEFAULT_OUTPUT_FILES.get(format, default_suffix)

        input_desc = actual_input_file.name if actual_input_file else "raw input"
        console.print(f"[blue]Converting {input_desc}...[/blue]")

        try:
            if format:
                result = ConfigTransformer.transform(
                    input_file=str(actual_input_file) if actual_input_file else None,
                    input_content=input_content,
                    provider=format,
                    llm_provider=preferred_provider,
                    encode_toon=encode_toon,
                    decode_toon=decode_toon,
                )

                if output and output.exists():
                    match output_action.lower():
                        case "skip":
                            console.print(f"[yellow]Skipping conversion: output file {output} already exists (action: skip)[/yellow]")
                            return
                        case "merge":
                            console.print(f"[blue]Merging with existing file: {output} (action: merge)[/blue]")

                            existing_data = json.loads(output.read_text(encoding="utf-8"))
                            new_data = json.loads(result)
                            existing_data.update(new_data)
                            result = json.dumps(existing_data, indent=2)
                        case _:
                            console.print(f"[blue]Will overwrite existing file: {output} (action: overwrite)[/blue]")

                if output:
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(result, encoding="utf-8")

                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")
                    if verbose:
                        console.print("\n[bold blue]Converted Configuration:[/bold blue]")
                        console.print(result)
                else:
                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{actual_input_file or 'raw input'}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                    console.print("[green]SUCCESS[/green] Output: [green]No output file specified (result generated)[/green]")
                    console.print("\n[bold blue]Converted Configuration:[/bold blue]")
                    console.print(result)
            else:
                console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                if format:
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                if output:
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")
                    if verbose:
                        console.print("\n[bold blue]Converted Configuration:[/bold blue]")
                        console.print(result)
        except Exception as exc:
            console.print(f"[red]Error during conversion:[/red] {str(exc)}")
            raise typer.Exit(1)

        console.print("\n[bold green]SUCCESS Conversion completed successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Conversion cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as exc:
        console.print(f"\n[red]Error:[/red] {str(exc)}")
        raise typer.Exit(1)
        """
        # Handle input source (file or content)
        if input_content is not None:
            # Using raw content input
            actual_input_file = None
        else:
            # Using file input
            actual_input_file = input_file
            input_content = None

        if interactive:
            console.print(Panel.fit("Interactive Conversion Mode", style="bold blue"))

            if not format:
                format = CliPrompt.select_format()

            if not output:
                if format and format in PROVIDER_DEFAULT_OUTPUT_FILES:
                    suggested_output = PROVIDER_DEFAULT_OUTPUT_FILES[format]
                else:
                    suggested_output = input_file.with_suffix(".mcp.json")

                output = Path(Prompt.ask("Enter output file path", default=str(suggested_output)))

            if not Confirm.ask(
                f"\nConvert [cyan]{input_file}[/cyan] → [green]{output}[/green]",
                default=True,
            ):
                console.print("[yellow]Conversion cancelled.[/yellow]")
                raise typer.Exit(0)

        if format and not validate_format_choice(format):
            valid_formats = ", ".join(PROVIDER_DEFAULT_OUTPUT_FILES.keys())
            console.print(f"[red]Error:[/red] Invalid format '{format}'. Choose from: {valid_formats}")
            raise typer.Exit(1)

        if format and not validate_format_choice(format):
            console.print(f"[red]Error:[/red] Invalid format '{format}'. Choose from: claude, gemini, vscode, opencode")
            raise typer.Exit(1)

        if not validate_output_action(output_action):
            console.print("[red]Error:[/red] Invalid output action. Choose from: overwrite, skip, merge")
            raise typer.Exit(1)

        if not output and format:
            default_suffix = input_file.with_suffix(".mcp.json") if input_file else Path("input.mcp.json")
            output = PROVIDER_DEFAULT_OUTPUT_FILES.get(format, default_suffix)

        input_desc = actual_input_file.name if actual_input_file else "raw input"
        console.print(f"[blue]Converting {input_desc}...[/blue]")

        try:
            if format:
                result = ConfigTransformer.transform(
                    input_file=str(actual_input_file) if actual_input_file else None,
                    input_content=input_content,
                    provider=format,
                    llm_provider=preferred_provider,
                    encode_toon=encode_toon,
                    decode_toon=decode_toon,
                )

                if output and output.exists():
                    match output_action.lower():
                        case "skip":
                            console.print(f"[yellow]Skipping conversion: output file {output} already exists (action: skip)[/yellow]")
                            return
                        case "merge":
                            console.print(f"[blue]Merging with existing file: {output} (action: merge)[/blue]")

                            existing_data = json.loads(output.read_text(encoding="utf-8"))
                            new_data = json.loads(result)
                            existing_data.update(new_data)
                            result = json.dumps(existing_data, indent=2)
                        case _:
                            console.print(f"[blue]Will overwrite existing file: {output} (action: overwrite)[/blue]")

                if output:
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(result, encoding="utf-8")

                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")
                    if verbose:
                        console.print("\n[bold blue]Converted Configuration:[/bold blue]")
                        console.print(result)
                else:
                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{actual_input_file or 'raw input'}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                    console.print("[green]SUCCESS[/green] Output: [green]No output file specified (result generated)[/green]")
                    console.print("\n[bold blue]Converted Configuration:[/bold blue]")
                    console.print(result)
            else:
                console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                if format:
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                if output:
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")
                    if verbose:
                        console.print("\n[bold blue]Converted Configuration:[/bold blue]")
                        console.print(result)
        except Exception as exc:
            console.print(f"[red]Error during conversion:[/red] {str(exc)}")
            raise typer.Exit(1)

        console.print("\n[bold green]SUCCESS Conversion completed successfully![/bold green]")
    """
