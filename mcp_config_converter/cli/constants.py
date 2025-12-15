from __future__ import annotations

from pathlib import Path

PROVIDER_DEFAULT_OUTPUT_FILES: dict[str, Path] = {
    "github-copilot-cli": Path(".vscode/mcp.json"),
    "vscode": Path(".vscode/mcp.json"),
    "gemini": Path(".gemini/mcp.json"),
    "claude": Path("mcp.json"),
    "codex": Path(".mcp.json"),
    "opencode": Path("opencode.json"),
}
SUPPORTED_PROVIDERS: list[str] = [
    "claude",
    "gemini",
    "vscode",
    "opencode",
]
VALID_FORMATS: list[str] = list(PROVIDER_DEFAULT_OUTPUT_FILES.keys())
VALID_OUTPUT_ACTIONS: list[str] = ["overwrite", "skip", "merge"]
