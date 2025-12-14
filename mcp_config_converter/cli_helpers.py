"""Helper utilities for CLI operations."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from rich.console import Console
from rich.prompt import Prompt

T = TypeVar("T")

console = Console()


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


def select_format(formats: list[str] | None = None, default: str = "json") -> str:
    """Interactively select an output format.

    Args:
        formats: List of available formats
        default: Default format selection

    Returns:
        Selected format
    """
    if formats is None:
        formats = ["json", "yaml", "toml"]

    return Prompt.ask(
        "Select output format",
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
    """Validate a format choice.

    Args:
        format: Format name to validate

    Returns:
        True if valid, False otherwise
    """
    valid_formats = ["json", "yaml", "toml"]
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
