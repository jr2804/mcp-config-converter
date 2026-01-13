from __future__ import annotations

import os
from collections import defaultdict
from enum import StrEnum
from pathlib import Path

from mcp_config_converter.types import OutputAction, ProviderConfig


class RichHelpPanel(StrEnum):
    OTHER = "Other Options"
    LLM = "LLM Parameters"


class EnvVarName(StrEnum):
    """Environment variable names for CLI configuration."""

    LLM_BASE_URL = "MCP_CONFIG_CONF_LLM_BASE_URL"
    LLM_PROVIDER = "MCP_CONFIG_CONF_LLM_PROVIDER"
    LLM_MODEL = "MCP_CONFIG_CONF_LLM_MODEL"
    LLM_API_KEY = "MCP_CONFIG_CONF_API_KEY"
    LLM_CACHE_ENABLED = "MCP_CONFIG_CONF_LLM_CACHE_ENABLED"
    LLM_CHECK_PROVIDER_ENDPOINT = "MCP_CONFIG_CONF_LLM_CHECK_PROVIDER_ENDPOINT"
    MAX_TESTS = "MCP_CONFIG_CONF_MAX_TESTS"
    TEST_LLM_PROVIDERS = "MCP_CONFIG_CONF_TEST_LLM_PROVIDERS"


class DefaultOutputEnvVar(StrEnum):
    """Environment variable names for default output paths."""

    DEFAULT = "MCP_CONFIG_CONV_DEFAULT_OUTPUT"
    VSCODE = "MCP_CONFIG_CONV_VSCODE_DEFAULT_OUTPUT"
    GEMINI = "MCP_CONFIG_CONV_GEMINI_DEFAULT_OUTPUT"
    CLAUDE = "MCP_CONFIG_CONV_CLAUDE_DEFAULT_OUTPUT"
    CODEX = "MCP_CONFIG_CONV_CODEX_DEFAULT_OUTPUT"
    OPENCODE = "MCP_CONFIG_CONV_OPENCODE_DEFAULT_OUTPUT"
    MISTRAL = "MCP_CONFIG_CONV_MISTRAL_DEFAULT_OUTPUT"
    QWEN = "MCP_CONFIG_CONV_QWEN_DEFAULT_OUTPUT"
    LLXPRT = "MCP_CONFIG_CONV_LLXPRT_DEFAULT_OUTPUT"
    CRUSH = "MCP_CONFIG_CONV_CRUSH_DEFAULT_OUTPUT"
    NCP = "MCP_CONFIG_CONV_NCP_DEFAULT_OUTPUT"


def get_default_output_path(provider: str) -> tuple[Path, str | None, str | None]:
    """Get default output path for a provider with environment variable override.

    Args:
        provider: Provider name (e.g., 'vscode', 'gemini')

    Returns:
        Tuple of (effective_path, env_var_name, env_var_value)
        - effective_path: Path to use (env var override or default)
        - env_var_name: Name of environment variable checked (or None)
        - env_var_value: Value from environment variable (or None)
    """
    # Try provider-specific environment variable first
    provider_upper = provider.upper()
    env_var_name = None
    env_var_value = None

    try:
        # Map provider name to enum member
        env_var_name = DefaultOutputEnvVar[provider_upper].value
        env_var_value = os.getenv(env_var_name)
    except KeyError:
        # Provider not in enum, try generic default
        env_var_name = DefaultOutputEnvVar.DEFAULT.value
        env_var_value = os.getenv(env_var_name)

    # Use environment variable value if set
    if env_var_value:
        return Path(env_var_value), env_var_name, env_var_value

    # Fall back to default path
    default_path = PROVIDER_DEFAULT_OUTPUT_FILES[provider]
    return default_path, env_var_name, None


PROVIDER_DEFAULT_OUTPUT_FILES: defaultdict[str, Path] = defaultdict(
    lambda: Path("mcp.json"),
    {
        "vscode": Path(".vscode/mcp.json"),
        "gemini": Path(".gemini/mcp.json"),
        "claude": Path("mcp.json"),
        "codex": Path(".mcp.json"),
        "opencode": Path(".opencode/opencode.json"),
        "mistral": Path(".vibe/config.toml"),
        "qwen": Path(".qwen/settings.json"),
        "llxprt": Path(".llxprt/settings.json"),
        "crush": Path(".crush.json"),
        "ncp": Path(".ncp/all.json"),
    },
)

SUPPORTED_PROVIDERS: set[str] = {provider.value for provider in ProviderConfig}
VALID_OUTPUT_ACTIONS: set[str] = {action.value for action in OutputAction}


def convert_to_json(content: str, format_type: str) -> dict:
    """Convert content from various formats to JSON (Python dict).

    Args:
        content: String content to convert
        format_type: Format of the content ('json', 'yaml', 'toml')

    Returns:
        Python dict representing the JSON data

    Raises:
        ValueError: If format is unsupported or conversion fails
    """
    import json

    if format_type == "json":
        return json.loads(content)
    elif format_type == "yaml":
        try:
            import yaml

            return yaml.safe_load(content) or {}
        except ImportError:
            raise ValueError("PyYAML not installed. Please install with: pip install pyyaml")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parsing error: {str(e)}")
    elif format_type == "toml":
        try:
            import tomllib

            return tomllib.loads(content)
        except ImportError:
            try:
                import tomli

                return tomli.loads(content)
            except ImportError:
                raise ValueError("tomllib/tomli not installed. Please install with: pip install tomli")
        except Exception as e:
            raise ValueError(f"TOML parsing error: {str(e)}")
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def convert_from_json(data: dict, format_type: str) -> str:
    """Convert Python dict to various formats.

    Args:
        data: Python dict to convert
        format_type: Target format ('json', 'yaml', 'toml')

    Returns:
        String content in the target format

    Raises:
        ValueError: If format is unsupported or conversion fails
    """
    import json

    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "yaml":
        try:
            import yaml

            return yaml.dump(data, sort_keys=False, indent=2)
        except ImportError:
            raise ValueError("PyYAML not installed. Please install with: pip install pyyaml")
    elif format_type == "toml":
        try:
            import tomli_w

            return tomli_w.dumps(data)
        except ImportError:
            raise ValueError("tomli_w not installed. Please install with: pip install tomli_w")
    else:
        raise ValueError(f"Unsupported format: {format_type}")
