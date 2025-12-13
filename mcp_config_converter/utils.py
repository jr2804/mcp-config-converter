"""Utility functions for MCP Config Converter."""

import os
from pathlib import Path
from typing import Any, Dict, Optional


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
    return Path(file_path).suffix.lstrip('.')
