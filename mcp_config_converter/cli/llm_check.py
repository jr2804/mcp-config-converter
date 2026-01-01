"""LLM provider check command."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from mcp_config_converter.cli import app, arguments
from mcp_config_converter.llm import LiteLLMClient, create_client_from_env, detect_available_providers
from mcp_config_converter.llm.client import PROVIDER_API_KEY_ENV_VARS, PROVIDER_DEFAULT_MODELS

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
        llm_provider_type: LiteLLM provider type (e.g., 'openai', 'anthropic')
        llm_api_key: API key for LLM provider
        llm_model: Model name for LLM provider
        verbose: Verbose output
    """
    try:
        console.print("[bold blue]LiteLLM Provider Status Check[/bold blue]\n")

        # Check if custom configuration provided
        if llm_provider_type or llm_api_key or llm_model or llm_base_url:
            console.print("[cyan]Custom Configuration Provided:[/cyan]")
            client = LiteLLMClient(
                provider=llm_provider_type,
                api_key=llm_api_key,
                model=llm_model,
                base_url=llm_base_url,
            )
            is_valid = client.validate_config()
            status = "[green]✓ Valid[/green]" if is_valid else "[red]✗ Invalid[/red]"
            console.print(f"  Provider: {client.provider or 'auto'}")
            console.print(f"  Model: {client.model}")
            console.print(f"  Status: {status}\n")

        # Create table for available providers
        table = Table(title="Available LiteLLM Providers", show_header=True, header_style="bold magenta")
        table.add_column("Provider", style="cyan", no_wrap=True)
        table.add_column("Default Model", style="green")
        table.add_column("API Key Source", style="yellow")
        table.add_column("Status", style="yellow")

        # Detect available providers
        available_providers = detect_available_providers()
        available_provider_names = {p[0] for p in available_providers}

        # Show all known providers
        for provider_name in sorted(PROVIDER_DEFAULT_MODELS.keys()):
            default_model = PROVIDER_DEFAULT_MODELS[provider_name]

            # Check if provider is configured
            if provider_name in available_provider_names:
                # Find the API key source
                api_key_source = "Configured"
                for provider, _api_key in available_providers:
                    if provider == provider_name:
                        # Find which env var was used
                        env_vars = PROVIDER_API_KEY_ENV_VARS.get(provider_name, [])
                        for env_var in env_vars:
                            import os
                            if os.getenv(env_var):
                                api_key_source = env_var
                                break
                        break

                if not PROVIDER_API_KEY_ENV_VARS.get(provider_name):
                    api_key_source = "N/A (Local)"

                table.add_row(
                    provider_name,
                    default_model,
                    api_key_source,
                    "[green]✓ Available[/green]"
                )
            else:
                # Not configured
                env_vars = PROVIDER_API_KEY_ENV_VARS.get(provider_name, [])
                if env_vars:
                    api_key_source = f"Missing ({', '.join(env_vars)})"
                    status = "[yellow]⚠ Not Configured[/yellow]"
                else:
                    api_key_source = "N/A (Local)"
                    status = "[yellow]⚠ Not Available[/yellow]"

                table.add_row(
                    provider_name,
                    default_model,
                    api_key_source,
                    status
                )

        console.print(table)

        # Show auto-selected provider
        console.print("\n[cyan]Auto-Selection:[/cyan]")
        try:
            auto_client = create_client_from_env()
            if auto_client:
                console.print(f"  Provider: [green]{auto_client.provider or 'auto'}[/green]")
                console.print(f"  Model: [green]{auto_client.model}[/green]")
            else:
                console.print("  [yellow]No provider auto-selected (no API keys found)[/yellow]")
        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")

        console.print(f"\n[dim]Found {len(available_providers)} configured provider(s)[/dim]")

        if verbose:
            console.print("\n[cyan]LiteLLM Documentation:[/cyan]")
            console.print("  https://docs.litellm.ai/docs/providers")

    except Exception as e:
        console.print(f"[red]Error checking LLM providers: {e}[/red]")
        if verbose:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)

