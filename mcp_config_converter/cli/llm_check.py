"""LLM provider check command."""

from __future__ import annotations

import logging
import os
import traceback
from typing import Annotated

import typer
from litellm import check_valid_key
from litellm.exceptions import (
    APIConnectionError,
    RateLimitError,
    ServiceUnavailableError,
)
from rich.console import Console
from rich.table import Table

from mcp_config_converter.cli import app, arguments
from mcp_config_converter.llm import (
    PROVIDER_API_KEY_ENV_VARS,
    PROVIDER_DEFAULT_MODELS,
    LiteLLMClient,
    create_client_from_env,
    detect_available_providers,
    get_provider_cost,
)

console = Console()
logger = logging.getLogger(__name__)


def check_provider_auth(provider: str, api_key: str | None, default_model: str | int) -> tuple[bool, str]:
    """Check if API key is valid for provider.

    Args:
        provider: Provider name
        api_key: API key to validate
        default_model: Default model for this provider (str or int index)

    Returns:
        Tuple of (is_valid, status_message)
    """
    if not api_key:
        return (False, "Not Configured")

    if provider == "ollama":
        return (False, "N/A (Local)")

    model_str = str(default_model)
    if isinstance(default_model, int):
        try:
            temp_client = LiteLLMClient(provider=provider)
            resolved_models = temp_client.get_available_models()
            if resolved_models and len(resolved_models) > abs(default_model):
                model_str = resolved_models[default_model]
            else:
                logger.debug(f"Could not resolve model index {default_model} for provider {provider}")
                return (False, "Error")
        except Exception as e:
            logger.debug(f"Could not resolve model for {provider}: {e}")
            return (False, "Error")

    try:
        is_valid = check_valid_key(model=f"{provider}/{model_str}", api_key=api_key)
        if is_valid:
            return (True, "Available")
        else:
            return (False, "Not allowed")
    except (APIConnectionError, ServiceUnavailableError) as e:
        console.print(f"[yellow]Warning: Network error checking {provider}: {e}[/yellow]")
        return (False, "Connection Error")
    except RateLimitError:
        console.print(f"[yellow]Warning: Rate limited checking {provider}[/yellow]")
        return (False, "Rate Limited")
    except Exception as e:
        console.print(f"[yellow]Warning: Error checking {provider}: {e}[/yellow]")
        return (False, "Error")


@app.command(name="llm-check")
def llm_check(
    ctx: typer.Context,
    llm_base_url: str | None = arguments.LlmBaseUrlOpt,
    llm_provider_type: str | None = arguments.LlmProviderTypeOpt,
    llm_api_key: str | None = arguments.LlmApiKeyOpt,
    llm_model: str | None = arguments.LlmModelOpt,
    no_auth_check: bool = arguments.NoAuthCheckOpt,
    verbose: bool = arguments.VerboseOpt,
    version: Annotated[bool | None, arguments.VersionOpt] = None,
) -> None:
    """Check LLM provider availability and configuration.

    Args:
        ctx: Typer context
        llm_base_url: Custom base URL for LLM provider
        llm_provider_type: LiteLLM provider type (e.g., 'openai', 'anthropic')
        llm_api_key: API key for LLM provider
        llm_model: Model name or index for LLM provider
        no_auth_check: Skip API key authentication check
        verbose: Verbose output
        version: Show version and exit
    """
    try:
        console.print("[bold blue]LiteLLM Provider Status Check[/bold blue]\n")

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

        table = Table(title="Available LiteLLM Providers", show_header=True, header_style="bold magenta")
        table.add_column("Provider", style="cyan", no_wrap=True)
        table.add_column("Default Model", style="green")
        table.add_column("Cost Factor", style="blue")
        table.add_column("Env Var Name", style="magenta")
        table.add_column("API Key Source", style="yellow")
        table.add_column("Status", style="yellow")

        available_providers = detect_available_providers()
        available_provider_names = {p[0] for p in available_providers}
        available_provider_map = {p[0]: p[1] for p in available_providers}

        auth_cache: dict[str, tuple[bool, str]] = {}

        if not no_auth_check and available_providers:
            console.print("[dim]Checking API key authentication...[/dim]\n")

        for provider_name in sorted(PROVIDER_DEFAULT_MODELS.keys()):
            default_model = PROVIDER_DEFAULT_MODELS[provider_name]
            default_model_str = str(default_model)

            if provider_name in available_provider_names:
                api_key = available_provider_map.get(provider_name)

                api_key_source = "Configured"
                env_vars = PROVIDER_API_KEY_ENV_VARS.get(provider_name, [])
                for env_var in env_vars:
                    if os.getenv(env_var):
                        api_key_source = env_var
                        break

                if not env_vars:
                    api_key_source = "N/A (Local)"

                cost_factor = get_provider_cost(provider_name)
                env_var_name = f"MCP_CONVERT_CONF_{provider_name.upper()}_COST"

                if no_auth_check:
                    status = "[green]✓ Available[/green]"
                else:
                    if provider_name not in auth_cache:
                        auth_cache[provider_name] = check_provider_auth(provider_name, api_key, default_model)
                    is_valid, auth_status = auth_cache[provider_name]
                    if is_valid:
                        status = "[green]✓ Available[/green]"
                    elif auth_status == "Not Configured":
                        status = "[yellow]⚠ Not Configured[/yellow]"
                    elif auth_status == "N/A (Local)":
                        status = "[yellow]⚠ Not Available[/yellow]"
                    else:
                        status = f"[red]✗ {auth_status}[/red]"

                table.add_row(
                    provider_name,
                    default_model_str,
                    str(cost_factor),
                    env_var_name,
                    api_key_source,
                    status,
                )
            else:
                env_vars = PROVIDER_API_KEY_ENV_VARS.get(provider_name, [])
                if env_vars:
                    api_key_source = f"Missing ({', '.join(env_vars)})"
                    status = "[yellow]⚠ Not Configured[/yellow]"
                else:
                    api_key_source = "N/A (Local)"
                    status = "[yellow]⚠ Not Available[/yellow]"

                cost_factor = get_provider_cost(provider_name)
                env_var_name = f"MCP_CONVERT_CONF_{provider_name.upper()}_COST"

                table.add_row(
                    provider_name,
                    default_model_str,
                    str(cost_factor),
                    env_var_name,
                    api_key_source,
                    status,
                )

        console.print(table)

        console.print("\n[cyan]Auto-Selection:[/cyan]")
        try:
            auto_client = create_client_from_env()
            if auto_client:
                console.print(f"  Provider: [green]{auto_client.provider or 'auto'}[/green]")
                console.print(f"  Model: [green]{auto_client.model}[/green]")
            else:
                console.print("  [yellow]No provider auto-selected (no API keys found)[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

        console.print(f"\n[dim]Found {len(available_providers)} configured provider(s)[/dim]")

        if verbose:
            console.print("\n[cyan]LiteLLM Documentation:[/cyan]")
            console.print("  https://docs.litellm.ai/docs/providers")

    except Exception as e:
        console.print(f"[red]Error checking LLM providers: {e}[/red]")
        if verbose:
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)
