"""Helper utilities for CLI operations."""

import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, TypeVar

from rich.console import Console
from rich.prompt import Prompt

T = TypeVar("T")

console = Console()

# Mapping of provider types to their default output filenames
PROVIDER_DEFAULT_OUTPUT_FILES = {
    "github-copilot-cli": Path(".vscode/mcp.json"),
    "vscode": Path(".vscode/mcp.json"),
    "gemini": Path(".gemini/mcp.json"),
    "claude": Path("mcp.json"),
    "codex": Path(".mcp.json"),
    "opencode": Path("opencode.json"),
}


def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)) -> Callable:
    """Decorator to retry a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None

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

            # If we get here, all retries failed
            raise last_exception

        return wrapper

    return decorator


def select_provider(providers: list[str] | None = None, default: str = "claude") -> str:
    """Interactively select an LLM provider.

    Args:
        providers: List of available providers
        default: Default provider selection

    Returns:
        Selected provider name
    """
    if providers is None:
        providers = ["claude", "gemini", "vscode", "opencode"]

    return Prompt.ask(
        "Select target LLM provider",
        choices=providers,
        default=default,
    )


def select_format(formats: list[str] | None = None, default: str = "claude") -> str:
    """Interactively select an output format (actually a provider type).

    Args:
        formats: List of available formats
        default: Default format selection

    Returns:
        Selected format
    """
    if formats is None:
        formats = list(PROVIDER_DEFAULT_OUTPUT_FILES.keys())

    return Prompt.ask(
        "Select target output format (provider type)",
        choices=formats,
        default=default,
    )


def validate_provider_choice(provider: str) -> bool:
    """Validate a provider choice.

    Args:
        provider: Provider name to validate

    Returns:
        True if valid, False otherwise
    """
    valid_providers = ["claude", "gemini", "vscode", "opencode"]
    return provider in valid_providers


def validate_format_choice(format: str) -> bool:
    """Validate a format choice (provider type).

    Args:
        format: Format name to validate

    Returns:
        True if valid, False otherwise
    """
    valid_formats = list(PROVIDER_DEFAULT_OUTPUT_FILES.keys())
    return format in valid_formats


def get_provider_config(provider: str) -> dict[str, Any]:
    """Get default configuration for a provider.

    Args:
        provider: Provider name

    Returns:
        Provider configuration dictionary
    """
    configs = {
        "claude": {
            "name": "Claude",
            "api_base": "https://api.anthropic.com",
        },
        "gemini": {
            "name": "Gemini",
            "api_base": "https://generativelanguage.googleapis.com",
        },
        "vscode": {
            "name": "VS Code",
            "type": "editor_plugin",
        },
        "opencode": {
            "name": "OpenCode",
            "type": "editor_plugin",
        },
    }
    return configs.get(provider, {})


def validate_output_action(action: str) -> bool:
    """Validate the output action choice.

    Args:
        action: Action to validate ('overwrite', 'skip', 'merge')

    Returns:
        True if valid, False otherwise
    """
    valid_actions = ["overwrite", "skip", "merge"]
    return action.lower() in valid_actions


def create_llm_provider(
    provider_type: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> Any:
    """Create an LLM provider based on configuration.

    Args:
        provider_type: LLM provider type ('openai', 'anthropic', or specific provider name)
        base_url: Custom base URL for the provider
        api_key: API key for the provider
        model: Model name to use

    Returns:
        An instance of BaseLLMProvider or None if no provider specified

    Raises:
        ValueError: If provider_type is invalid or configuration is incomplete
        ImportError: If required dependencies are not installed
    """
    if not provider_type:
        return None

    provider_type = provider_type.lower()

    # First try to get provider from registry (for registered providers)
    from mcp_config_converter.llm import ProviderRegistry

    try:
        return ProviderRegistry.create_provider(
            provider_type,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
    except ValueError:
        # Provider not found in registry, try dynamic creation
        pass

    # Handle dynamic provider creation for custom OpenAI/Anthropic compatible endpoints
    if provider_type == "openai":
        try:
            from mcp_config_converter.llm.openai import OpenAIProvider

            return OpenAIProvider(
                api_key=api_key,
                model=model or "gpt-4-turbo",
                base_url=base_url,
            )
        except ImportError as e:
            raise ImportError(f"OpenAI provider requires 'openai' package: {e}")

    elif provider_type == "anthropic":
        try:
            from mcp_config_converter.llm.claude import ClaudeProvider

            # Note: Anthropic API doesn't support custom base_url in the same way as OpenAI
            # We'll create a standard ClaudeProvider for now
            return ClaudeProvider(
                api_key=api_key,
                model=model or "claude-3-5-sonnet-20241022",
            )
        except ImportError as e:
            raise ImportError(f"Anthropic provider requires 'anthropic' package: {e}")

    else:
        # Unknown provider type
        raise ValueError(f"Unknown provider type: {provider_type}. Available providers: {', '.join(ProviderRegistry.list_providers())}")
