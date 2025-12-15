from enum import StrEnum


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


class ConfigFormat(StrEnum):
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    TOON = "toon"
    TEXT = "text"
