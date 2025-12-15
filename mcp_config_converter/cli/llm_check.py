from __future__ import annotations

import typer
from rich.table import Table

from mcp_config_converter.cli import arguments
from mcp_config_converter.cli.utils import configure_llm_provider, console
from mcp_config_converter.llm import ProviderRegistry

try:
    from openai import OpenAI  # noqa: F401

    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False


def llm_check(
    ctx: typer.Context,
    llm_base_url: str | None = arguments.llm_base_url_option(),
    llm_provider_type: str | None = arguments.llm_provider_type_option(),
    llm_model: str | None = arguments.llm_model_option(),
    preferred_provider: str = arguments.preferred_provider_option(),
    verbose: bool = False,
) -> None:
    """Check the status of all available LLM providers.

    This command provides a comprehensive overview of all registered LLM providers,
    displaying their availability, authentication status, and configuration details
    in a tabular format. Use --verbose to see preferred provider selection details.
    """
    try:
        # Show preferred provider selection info if verbose
        if verbose:
            preferred_provider = preferred_provider  # Use the parameter directly
            if preferred_provider == "auto":
                try:
                    from mcp_config_converter.cli.utils import select_auto_provider

                    auto_provider = select_auto_provider()
                    console.print(f"[blue]Auto-selected LLM provider: {auto_provider}[/blue]")
                except ValueError as e:
                    console.print(f"[yellow]Warning: {e}[/yellow]")
            else:
                console.print(f"[blue]Using preferred LLM provider: {preferred_provider}[/blue]")

        table = Table(title="LLM Provider Status", show_header=True, header_style="bold blue")
        table.add_column("Provider", style="dim")
        table.add_column("Model", style="dim")
        table.add_column("Availability", justify="center")
        table.add_column("Authentication", justify="center")

        providers = ProviderRegistry.list_providers()

        for provider_name in providers:
            provider_class = ProviderRegistry.get_provider(provider_name)

            if provider_class is None:
                continue

            provider_display_name = getattr(provider_class, "PROVIDER_NAME", provider_name)
            default_model = getattr(provider_class, "DEFAULT_MODEL", "default")
            requires_api_key = getattr(provider_class, "REQUIRES_API_KEY", True)

            available = False
            authenticated = False

            try:
                provider_instance = ProviderRegistry.create_provider(provider_name)
                available = provider_instance._create_client() is not None
                authenticated = provider_instance.validate_config()
            except Exception:
                available = False
                authenticated = False

            availability_status = "[green]ok[/green]" if available else "[red]failed[/red]"
            if not requires_api_key:
                auth_status = "[yellow]n/a[/yellow]" if available else "[red]failed[/red]"
            else:
                auth_status = "[green]ok[/green]" if authenticated else "[red]failed[/red]"

            table.add_row(
                provider_display_name,
                default_model,
                availability_status,
                auth_status,
            )

        if llm_base_url and llm_provider_type and llm_model:
            custom_available = False
            custom_auth = False
            if _OPENAI_AVAILABLE:
                custom_available = True
                try:
                    custom_provider = ProviderRegistry.create_provider(
                        llm_provider_type,
                        base_url=llm_base_url,
                        model=llm_model,
                    )
                    custom_auth = custom_provider.validate_config()
                except Exception:
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
    except Exception as exc:
        console.print(f"\n[red]Error:[/red] {str(exc)}")
        raise typer.Exit(1)
