"""Utility functions for MCP Config Converter."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()


def get_env_variable(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable safely.

    Args:
        name: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default
    """
    return os.getenv(name, default)


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, creating if necessary.

    Args:
        path: Directory path

    Returns:
        Path to directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Dictionary to merge on top

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def validate_file_exists(file_path: Path) -> bool:
    """Validate that a file exists.

    Args:
        file_path: Path to file

    Returns:
        True if file exists
    """
    return Path(file_path).is_file()


def get_file_extension(file_path: Path) -> str:
    """Get file extension without leading dot.

    Args:
        file_path: Path to file

    Returns:
        File extension
    """
    return Path(file_path).suffix.lstrip(".")


def prompt_for_choice(
    message: str, choices: List[str], default: Optional[str] = None
) -> str:
    """Prompt user to select from a list of choices.

    Args:
        message: Prompt message
        choices: List of valid choices
        default: Default choice if user presses enter

    Returns:
        Selected choice
    """
    return Prompt.ask(message, choices=choices, default=default)


def prompt_for_confirmation(message: str, default: bool = False) -> bool:
    """Prompt user for yes/no confirmation.

    Args:
        message: Confirmation message
        default: Default value if user presses enter

    Returns:
        True if user confirms, False otherwise
    """
    return Confirm.ask(message, default=default)


def prompt_for_text(message: str, default: Optional[str] = None) -> str:
    """Prompt user for text input.

    Args:
        message: Prompt message
        default: Default value if user presses enter

    Returns:
        User input
    """
    return Prompt.ask(message, default=default)


def select_provider(default: str = "claude") -> str:
    """Interactive provider selection.

    Args:
        default: Default provider

    Returns:
        Selected provider
    """
    providers = ["claude", "gemini", "vscode", "opencode"]
    return prompt_for_choice(
        "Select target LLM provider", choices=providers, default=default
    )


def select_format(default: str = "json") -> str:
    """Interactive format selection.

    Args:
        default: Default format

    Returns:
        Selected format
    """
    formats = ["json", "yaml", "toml"]
    return prompt_for_choice("Select output format", choices=formats, default=default)
