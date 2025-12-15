from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from mcp_config_converter.cli import arguments, constants
from mcp_config_converter.cli.utils import (
    CliPrompt,
    configure_llm_provider,
    console,
    validate_format_choice,
    validate_output_action,
    validate_provider_choice,
)

PROVIDER_DEFAULT_OUTPUT_FILES = constants.PROVIDER_DEFAULT_OUTPUT_FILES


def get_input_file_argument() -> Path:
    return arguments.input_file_argument()


def get_output_option() -> Path | None:
    return arguments.output_option()


def get_format_option() -> str | None:
    return arguments.format_option()


def get_provider_option() -> str | None:
    return arguments.provider_option()


def get_interactive_option() -> bool:
    return arguments.interactive_option()


def get_output_action_option() -> str:
    return arguments.output_action_option()


def convert(
    ctx: typer.Context,
    input_file: Path | None = None,
    output: Path | None = None,
    format: str | None = None,
    provider: str | None = None,
    interactive: bool = False,
    output_action: str | None = None,
    preferred_provider: str = arguments.preferred_provider_option(),
    verbose: bool = False,
) -> None:
    """Convert an MCP configuration file to a supported format.

    Args:
        ctx: Typer context
        input_file: Input file path
        output: Output file path
        format: Output format
        provider: Target LLM provider
        interactive: Run in interactive mode
        output_action: Action when output file exists
    """
    try:
        verbose = ctx.obj.get("verbose", False)
        configure_llm_provider(ctx, verbose=verbose)

        # Handle default values
        if input_file is None:
            input_file = get_input_file_argument()
        if output is None:
            output = get_output_option()
        if format is None:
            format = get_format_option()
        if provider is None:
            provider = get_provider_option()
        if interactive is False:
            interactive = get_interactive_option()
        if output_action is None:
            output_action = get_output_action_option()

        if interactive:
            console.print(Panel.fit("Interactive Conversion Mode", style="bold blue"))

            if not format:
                format = CliPrompt.select_format()

            if not provider:
                provider = CliPrompt.select_provider()

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

        if provider and not validate_provider_choice(provider):
            console.print(f"[red]Error:[/red] Invalid provider '{provider}'. Choose from: claude, gemini, vscode, opencode")
            raise typer.Exit(1)

        if not validate_output_action(output_action):
            console.print("[red]Error:[/red] Invalid output action. Choose from: overwrite, skip, merge")
            raise typer.Exit(1)

        if not output and format:
            output = PROVIDER_DEFAULT_OUTPUT_FILES.get(format, input_file.with_suffix(".mcp.json"))

        console.print(f"[blue]Converting {input_file.name}...[/blue]")

        try:
            if format:
                result = ConfigTransformer.transform(str(input_file), None, format)

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
                else:
                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                    console.print("[green]SUCCESS[/green] Output: [green]No output file specified (result generated)[/green]")
            else:
                console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                if provider:
                    console.print(f"[green]SUCCESS[/green] Target provider: [cyan]{provider}[/cyan]")
                if output:
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")
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

        # Handle default values
        if input_file is None:
            input_file = get_input_file_argument()
        if output is None:
            output = get_output_option()
        if format is None:
            format = get_format_option()
        if provider is None:
            provider = get_provider_option()
        if interactive is False:
            interactive = get_interactive_option()
        if output_action is None:
            output_action = get_output_action_option()

        if interactive:
            console.print(Panel.fit("Interactive Conversion Mode", style="bold blue"))

            if not format:
                format = CliPrompt.select_format()

            if not provider:
                provider = CliPrompt.select_provider()

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

        if provider and not validate_provider_choice(provider):
            console.print(f"[red]Error:[/red] Invalid provider '{provider}'. Choose from: claude, gemini, vscode, opencode")
            raise typer.Exit(1)

        if not validate_output_action(output_action):
            console.print("[red]Error:[/red] Invalid output action. Choose from: overwrite, skip, merge")
            raise typer.Exit(1)

        if not output and format:
            output = PROVIDER_DEFAULT_OUTPUT_FILES.get(format, input_file.with_suffix(".mcp.json"))

        console.print(f"[blue]Converting {input_file.name}...[/blue]")

        try:
            if format:
                result = ConfigTransformer.transform(str(input_file), None, format)

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
                else:
                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                    console.print("[green]SUCCESS[/green] Output: [green]No output file specified (result generated)[/green]")
            else:
                console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                if provider:
                    console.print(f"[green]SUCCESS[/green] Target provider: [cyan]{provider}[/cyan]")
                if output:
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")
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
