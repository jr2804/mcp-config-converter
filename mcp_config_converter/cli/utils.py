from __future__ import annotations

import time
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

import typer
from rich.console import Console
from rich.prompt import Prompt

from mcp_config_converter.cli import constants, registry
from mcp_config_converter.llm import ProviderRegistry

T = TypeVar("T")
console = Console()


def get_context_llm_config(ctx: typer.Context | None) -> dict[str, str | None]:
    if ctx is None:
        return {}

    if not hasattr(ctx, "obj") or ctx.obj is None:
        return {}

    return ctx.obj.get("llm_config", {})


def select_auto_provider() -> str:
    """Select the first fully configured LLM provider automatically using ProviderRegistry order.

    Returns:
        Provider name if found

    Raises:
        ValueError: If no providers are configured
    """
    providers = ProviderRegistry.list_providers()

    for provider_name in providers:
        try:
            provider_class = ProviderRegistry.get_provider(provider_name)
            if provider_class is None:
                continue

            # Create instance to check configuration
            provider_instance = provider_class()
            if provider_instance.validate_config():
                return provider_name
        except Exception:
            continue

    raise ValueError("No fully configured LLM providers found. Please configure at least one provider with API keys and required dependencies.")


def configure_llm_provider(ctx: typer.Context | None, verbose: bool = False) -> None:
    llm_config = get_context_llm_config(ctx)
    provider_type = llm_config.get("provider_type")

    # Check for preferred provider selection
    preferred_provider = ctx.obj.get("preferred_provider", "auto") if ctx else "auto"

    if preferred_provider == "auto":
        try:
            auto_provider = select_auto_provider()
            provider_type = auto_provider
            if verbose:
                console.print(f"[blue]Auto-selected LLM provider: {provider_type}[/blue]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
    elif preferred_provider != "auto":
        # Validate that the preferred provider exists
        if preferred_provider not in ProviderRegistry.list_providers():
            available_providers = ", ".join(ProviderRegistry.list_providers())
            console.print(f"[red]Error: Unknown provider '{preferred_provider}'. Available providers: {available_providers}[/red]")
            raise typer.Exit(1)

        provider_type = preferred_provider
        if verbose:
            console.print(f"[blue]Using preferred LLM provider: {provider_type}[/blue]")

    if not provider_type:
        # This should not happen with auto-selection, but keep as fallback
        console.print("[red]Error: No LLM provider specified or auto-selected[/red]")
        raise typer.Exit(1)

    try:
        created_provider = registry.create_llm_provider(
            provider_type=provider_type,
            base_url=llm_config.get("base_url"),
            api_key=llm_config.get("api_key"),
            model=llm_config.get("model"),
        )
        if created_provider is not None:
            if verbose:
                console.print(f"[blue]Using LLM provider: {provider_type}[/blue]")
        else:
            if verbose:
                console.print(f"[yellow]Warning: Could not create LLM provider: {provider_type}[/yellow]")
    except (ImportError, ValueError) as exc:
        console.print(f"[yellow]Warning: Could not create LLM provider: {exc}[/yellow]")
        raise typer.Exit(1)


class OutputAction(str, Enum):
    OVERWRITE = "overwrite"
    SKIP = "skip"
    MERGE = "merge"


class ValidationError(ValueError):
    pass


class ProviderConfig(str, Enum):
    CLAUDE = "claude"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    VSCODE = "vscode"
    OPENCODE = "opencode"


class CliPrompt:
    @staticmethod
    def select_provider(providers: list[str] | None = None, default: str = ProviderConfig.CLAUDE.value) -> str:
        if providers is None:
            providers = constants.SUPPORTED_PROVIDERS
        return Prompt.ask("Select target LLM provider", choices=providers, default=default)

    @staticmethod
    def select_format(formats: list[str] | None = None, default: str = constants.VALID_FORMATS[0]) -> str:
        if formats is None:
            formats = constants.VALID_FORMATS
        return Prompt.ask(
            "Select target output format (provider type)",
            choices=formats,
            default=default,
        )


# Mapping of provider types to their default output filenames is in constants.PROVIDER_DEFAULT_OUTPUT_FILES


def retry_with_backoff(
    max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0, exceptions: tuple[type[BaseException], ...] = (Exception,)
) -> Callable[..., T]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception: BaseException | None = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        console.print(f"[yellow]Attempt {attempt + 1}/{max_retries} failed: {str(e)}[/yellow]")
                        console.print(f"[dim]Retrying in {delay:.1f} seconds...[/dim]")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        console.print(f"[red]All {max_retries} retry attempts failed.[/red]")

            if last_exception is None:
                raise RuntimeError("No exception was caught during retry attempts")
            raise last_exception

        return wrapper

    return decorator


def validate_provider_choice(provider: str) -> bool:
    if provider == "auto":
        return True
    return provider in constants.SUPPORTED_PROVIDERS or provider in ProviderRegistry.list_providers()


def validate_format_choice(format_choice: str) -> bool:
    return format_choice in constants.VALID_FORMATS


def validate_output_action(action: str) -> bool:
    return action.lower() in constants.VALID_OUTPUT_ACTIONS


def get_provider_config(provider: str) -> dict[str, Any]:
    configs = {
        ProviderConfig.CLAUDE.value: {
            "name": "Claude",
            "api_base": "https://api.anthropic.com",
        },
        ProviderConfig.GEMINI.value: {
            "name": "Gemini",
            "api_base": "https://generativelanguage.googleapis.com",
        },
        ProviderConfig.MISTRAL.value: {
            "name": "Mistral",
            "api_base": "https://api.mistral.ai",
        },
        ProviderConfig.VSCODE.value: {
            "name": "VS Code",
            "type": "editor_plugin",
        },
        ProviderConfig.OPENCODE.value: {
            "name": "OpenCode",
            "type": "editor_plugin",
        },
    }
    return configs.get(provider, {})
