from enum import StrEnum

# Provider alias mapping - maps providers to their actual implementation
PROVIDER_ALIAS_MAP: dict[str, str] = {
    "qwen": "gemini",  # qwen uses the same spec as gemini
    "llxprt": "gemini",  # qwen uses the same spec as gemini
}


class OutputAction(StrEnum):
    OVERWRITE = "overwrite"
    SKIP = "skip"
    MERGE = "merge"


class ProviderConfig(StrEnum):
    CLAUDE = "claude"
    GEMINI = "gemini"
    CODEX = "codex"
    MISTRAL = "mistral"
    VSCODE = "vscode"
    OPENCODE = "opencode"
    QWEN = "qwen"
    LLXPRT = "llxprt"
    CRUSH = "crush"


class ConfigFormat(StrEnum):
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    TOON = "toon"
    TEXT = "text"
