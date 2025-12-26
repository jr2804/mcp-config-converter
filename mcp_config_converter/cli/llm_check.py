"""LLM provider check command."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from mcp_config_converter.cli import app, arguments
from mcp_config_converter.llm import create_provider, get_provider_info, list_providers, select_best_provider

console = Console()


@app.command(name="llm-check")
def llm_check(
    ctx: typer.Context,
    llm_base_url: str | None = arguments.LlmBaseUrlOpt,
    llm_provider_type: str | None = arguments.LlmProviderTypeOpt,
    llm_api_key: str | None = arguments.LlmApiKeyOpt,
    llm_model: str | None = arguments.LlmModelOpt,
    verbose: bool = arguments.VerboseOpt,
    version: Annotated[bool | None, arguments.VersionOpt] = None,
) -> None:
    """Check LLM provider availability and configuration.

    Args:
        ctx: Typer context
        llm_base_url: Custom base URL for LLM provider
        llm_provider_type: LLM provider type
        llm_api_key: API key for LLM provider
        llm_model: Model name for LLM provider
        verbose: Verbose output
    """
    try:
        console.print("[bold blue]LLM Provider Status Check[/bold blue]\n")

        # Check for custom provider configuration
        custom_provider_args = {}
        if llm_base_url:
            custom_provider_args["base_url"] = llm_base_url
        if llm_api_key:
            custom_provider_args["api_key"] = llm_api_key
        if llm_model:
            custom_provider_args["model"] = llm_model
        if llm_provider_type:
            custom_provider_args["provider_type"] = llm_provider_type

        # Create table
        table = Table(title="LLM Provider Status", show_header=True, header_style="bold magenta")
        table.add_column("Provider", style="cyan", no_wrap=True)
        table.add_column("Model", style="green")
        table.add_column("Nbr of Models", style="cyan", no_wrap=True)
        table.add_column("Availability", style="yellow")
        table.add_column("Authentication", style="yellow")
        table.add_column("Cost", style="blue")

        # Collect all provider data for sorting
        provider_data = []

        # Check all registered providers
        for provider_name in list_providers():
            provider_info = get_provider_info(provider_name)
            if not provider_info:
                continue

            try:
                # Try to create provider instance
                provider = provider_info.provider_class()
                availability = "[bold green]OK[/bold green]"
                model = provider.model or "default"

                # Get number of available models
                model_count = str(len(provider.available_models)) if provider.available_models is not None else "[bold red]n/a[/bold red]"

                # Check authentication
                authentication = "[bold green]OK[/bold green]" if provider.validate_config() else "[bold red]Failed[/bold red]"

            except Exception:
                availability = "[bold red]Failed[/bold red]"
                authentication = "[bold red]Failed[/bold red]"
                model = "[bold red]Failed[/bold red]"
                model_count = "[bold red]n/a[/bold red]"

            provider_data.append(
                {
                    "name": provider_name,
                    "model": model,
                    "model_count": model_count,
                    "availability": availability,
                    "authentication": authentication,
                    "cost": provider_info.cost if provider_info else 0,
                    "is_custom": False,
                }
            )

        # Check custom provider if configured
        if custom_provider_args:
            try:
                # Try to create custom provider
                custom_provider = create_provider("custom", **custom_provider_args)
                availability = "[bold green]OK[/bold green]"
                model = custom_provider.model or "custom"
                authentication = "[bold green]OK[/bold green]" if custom_provider.validate_config() else "[bold red]Failed[/bold red]"
                model_count = "[bold red]n/a[/bold red]"
                provider_data.append(
                    {
                        "name": "custom",
                        "model": model,
                        "model_count": model_count,
                        "availability": availability,
                        "authentication": authentication,
                        "cost": -1,  # Custom providers always have cost -1 (always selected)
                        "is_custom": True,
                    }
                )
            except Exception:
                provider_data.append(
                    {
                        "name": "custom",
                        "model": "[bold red]Failed[/bold red]",
                        "model_count": "[bold red]n/a[/bold red]",
                        "availability": "[bold red]Failed[/bold red]",
                        "authentication": "[bold red]Failed[/bold red]",
                        "cost": -1,
                        "is_custom": True,
                    }
                )

        # Sort by cost (increasing)
        provider_data.sort(key=lambda x: x["cost"])

        # Add sorted data to table
        for data in provider_data:
            table.add_row(
                data["name"],
                data["model"],
                data["model_count"],
                data["availability"],
                data["authentication"],
                str(data["cost"]),
            )

        console.print(table)

        # Check auto-selection
        if verbose:
            console.print("\n[bold blue]Auto-selection Test:[/bold blue]")
            try:
                best_provider = select_best_provider()
                console.print(f"[green]Auto-selected LLM provider: {best_provider.PROVIDER_NAME}[/green]")
                console.print(f"[green]Model: {best_provider.model or 'default'}[/green]")
                console.print(f"[green]Cost: {get_provider_info(best_provider.PROVIDER_NAME).cost}[/green]")
            except Exception as e:
                console.print(f"[red]Auto-selection failed: {str(e)}[/red]")

        console.print("\n[bold green]LLM provider check completed.[/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]LLM check cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)
