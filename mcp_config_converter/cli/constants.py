from __future__ import annotations

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
    LLM_PROVIDER_TYPE = "MCP_CONFIG_CONF_LLM_PROVIDER_TYPE"
    LLM_MODEL = "MCP_CONFIG_CONF_LLM_MODEL"
    LLM_API_KEY = "MCP_CONFIG_CONF_API_KEY"
    PREFERRED_PROVIDER = "MCP_CONFIG_CONF_PREFERRED_PROVIDER"
    MAX_TESTS = "MCP_CONFIG_CONF_MAX_TESTS"
    TEST_LLM_PROVIDERS = "MCP_CONFIG_CONF_TEST_LLM_PROVIDERS"


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
    },
)


SUPPORTED_PROVIDERS: set[str] = {provider.value for provider in ProviderConfig}
VALID_OUTPUT_ACTIONS: set[str] = {action.value for action in OutputAction}
