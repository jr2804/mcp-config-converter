from __future__ import annotations

from collections import defaultdict
from enum import StrEnum
from pathlib import Path

from mcp_config_converter.types import OutputAction, ProviderConfig


class RichHelpPanel(StrEnum):
    OTHER = "Other Options"
    LLM = "LLM Parameters"


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
    },
)


SUPPORTED_PROVIDERS: set[str] = {provider.value for provider in ProviderConfig}
VALID_OUTPUT_ACTIONS: set[str] = {action.value for action in OutputAction}
