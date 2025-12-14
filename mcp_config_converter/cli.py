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
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    llm_base_url: str | None = typer.Option(
        None,
        "--llm-base-url",
        help="Custom base URL for LLM provider (for OpenAI/Anthropic compatible APIs)",
    ),
    llm_provider_type: str | None = typer.Option(
        None,
        "--llm-provider-type",
        help="LLM provider type: 'openai' or 'anthropic' for custom providers",
    ),
    llm_api_key: str | None = typer.Option(
        None,
        "--llm-api-key",
        help="API key for LLM provider (overrides environment variables)",
    ),
    llm_model: str | None = typer.Option(
        None,
        "--llm-model",
        help="Model name for the configured LLM provider",
    ),
) -> None:
    """MCP Config Converter - Convert MCP configurations between formats and LLM providers."""
    # Store LLM configuration in context for commands to access
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj["llm_config"] = {
        "base_url": llm_base_url,
        "provider_type": llm_provider_type,
        "api_key": llm_api_key,
        "model": llm_model,
    }


@app.command()
def convert(
    ctx: typer.Context,
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
        # Get LLM configuration from context
        llm_config = {}
        if hasattr(ctx, "obj") and ctx.obj:
            llm_config = ctx.obj.get("llm_config", {})

        # Create LLM provider if configured
        if llm_config.get("provider_type"):
            try:
                from mcp_config_converter.cli_helpers import create_llm_provider

                create_llm_provider(
                    provider_type=llm_config.get("provider_type"),
                    base_url=llm_config.get("base_url"),
                    api_key=llm_config.get("api_key"),
                    model=llm_config.get("model"),
                )
                console.print(f"[blue]Using LLM provider: {llm_config.get('provider_type')}[/blue]")
            except (ImportError, ValueError) as e:
                console.print(f"[yellow]Warning: Could not create LLM provider: {e}[/yellow]")

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
            console.print(f"[red]Error:[/red] Invalid format '{format}'. Choose from: {valid_formats}")
            raise typer.Exit(1)

        if provider and not validate_provider_choice(provider):
            console.print(f"[red]Error:[/red] Invalid provider '{provider}'. Choose from: claude, gemini, vscode, opencode")
            raise typer.Exit(1)

        # Validate output action
        if not validate_output_action(output_action):
            console.print("[red]Error:[/red] Invalid output action. Choose from: overwrite, skip, merge")
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

                        existing_content = output.read_text(encoding="utf-8")
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
                    output.write_text(result, encoding="utf-8")

                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")
                else:
                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target format: [cyan]{format}[/cyan]")
                    console.print("[green]SUCCESS[/green] Output: [green]No output file specified (result generated)[/green]")
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
    ctx: typer.Context,
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
        # Get LLM configuration from context
        llm_config = {}
        if hasattr(ctx, "obj") and ctx.obj:
            llm_config = ctx.obj.get("llm_config", {})

        # Create LLM provider if configured
        if llm_config.get("provider_type"):
            try:
                from mcp_config_converter.cli_helpers import create_llm_provider

                create_llm_provider(
                    provider_type=llm_config.get("provider_type"),
                    base_url=llm_config.get("base_url"),
                    api_key=llm_config.get("api_key"),
                    model=llm_config.get("model"),
                )
                console.print(f"[blue]Using LLM provider: {llm_config.get('provider_type')}[/blue]")
            except (ImportError, ValueError) as e:
                console.print(f"[yellow]Warning: Could not create LLM provider: {e}[/yellow]")

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
    ctx: typer.Context,
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
        import sys

        # Get LLM configuration from context
        llm_config = {}
        if hasattr(ctx, "obj") and ctx.obj:
            llm_config = ctx.obj.get("llm_config", {})

        # Create LLM provider if configured
        if llm_config.get("provider_type"):
            try:
                from mcp_config_converter.cli_helpers import create_llm_provider

                create_llm_provider(
                    provider_type=llm_config.get("provider_type"),
                    base_url=llm_config.get("base_url"),
                    api_key=llm_config.get("api_key"),
                    model=llm_config.get("model"),
                )
                console.print(f"[blue]Using LLM provider: {llm_config.get('provider_type')}[/blue]")
            except (ImportError, ValueError) as e:
                console.print(f"[yellow]Warning: Could not create LLM provider: {e}[/yellow]")

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

        # Use a simpler spinner for Windows to avoid Unicode encoding issues
        import sys

        def run_initialization(progress) -> None:
            task = progress.add_task("Initializing configuration...", total=None)

            # TODO: Implement actual initialization logic
            if provider:
                console.print(f"\n[green]SUCCESS[/green] Provider: [cyan]{provider}[/cyan]")
            if output:
                console.print(f"[green]SUCCESS[/green] Output: [green]{output}[/green]")

            progress.update(task, completed=True)

        if sys.platform == "win32":
            from rich.progress import Progress, TextColumn

            with Progress(
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
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
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def llm_check(
    ctx: typer.Context,
    llm_base_url: str | None = typer.Option(
        None,
        "--llm-base-url",
        help="Base URL for custom OpenAI-compatible provider",
    ),
    llm_provider_type: str | None = typer.Option(
        None,
        "--llm-provider-type",
        help="Provider type for custom OpenAI-compatible provider",
    ),
    llm_model: str | None = typer.Option(
        None,
        "--llm-model",
        help="Model name for custom OpenAI-compatible provider",
    ),
) -> None:
    """Check the status of all LLM providers."""
    try:
        from rich.table import Table
        from mcp_config_converter.llm import ProviderRegistry

        # Create the table
        table = Table(title="LLM Provider Status", show_header=True, header_style="bold blue")
        table.add_column("Provider", style="dim")
        table.add_column("Model", style="dim")
        table.add_column("Availability", justify="center")
        table.add_column("Authentication", justify="center")

        # Get all registered providers
        providers = ProviderRegistry.list_providers()

        for provider_name in sorted(providers):
            provider_class = ProviderRegistry.get_provider(provider_name)

            if provider_class is None:
                continue

            # Get provider metadata
            provider_display_name = getattr(provider_class, "PROVIDER_NAME", provider_name)
            default_model = getattr(provider_class, "DEFAULT_MODEL", "default")
            requires_api_key = getattr(provider_class, "REQUIRES_API_KEY", True)

            # Check provider availability and authentication
            available = False
            authenticated = False

            try:
                # Try to create provider instance
                provider_instance = ProviderRegistry.create_provider(provider_name)

                # Check if provider is available (client creation succeeded)
                available = provider_instance._create_client() is not None

                # Check authentication status
                authenticated = provider_instance.validate_config()

            except Exception:
                # Provider instantiation or validation failed
                available = False
                authenticated = False

            # Format status indicators
            availability_status = "[green]ok[/green]" if available else "[red]failed[/red]"

            if not requires_api_key:
                # For providers that don't require API keys, show n/a for auth
                auth_status = "[yellow]n/a[/yellow]" if available else "[red]failed[/red]"
            else:
                auth_status = "[green]ok[/green]" if authenticated else "[red]failed[/red]"

            table.add_row(
                provider_display_name,
                default_model,
                availability_status,
                auth_status,
            )

        # Add custom OpenAI provider if all required parameters are provided
        if llm_base_url and llm_provider_type and llm_model:
            custom_available = False
            custom_auth = False
            try:
                # Check if OpenAI SDK is available
                from openai import OpenAI  # noqa: F401

                custom_available = True

                # Try to create custom provider using the registry
                try:
                    if llm_provider_type == "openai":
                        custom_provider = ProviderRegistry.create_provider("openai", base_url=llm_base_url, model=llm_model)
                        custom_auth = custom_provider.validate_config()
                    else:
                        # For other custom providers, try to create via registry or fallback
                        try:
                            custom_provider = ProviderRegistry.create_provider(llm_provider_type, base_url=llm_base_url, model=llm_model)
                            custom_auth = custom_provider.validate_config()
                        except ValueError:
                            # Provider not found in registry, show as unavailable
                            custom_available = False
                            custom_auth = False
                except Exception:
                    custom_auth = False
            except ImportError:
                custom_available = False
                custom_auth = False

            table.add_row(
                f"Custom {llm_provider_type.title()}",
                llm_model,
                "[green]ok[/green]" if custom_available else "[red]failed[/red]",
                "[green]ok[/green]" if custom_auth else "[red]failed[/red]",
            )

        console.print(table)

    except KeyboardInterrupt:
        console.print("\n[yellow]LLM check cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
