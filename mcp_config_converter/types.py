from enum import StrEnum


class OutputAction(StrEnum):
    OVERWRITE = "overwrite"
    SKIP = "skip"
    REPLACE = "replace"
    UPDATE = "update"


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


# Provider alias mapping - maps providers to their actual implementation
PROVIDER_ALIAS_MAP: dict[ProviderConfig | str, ProviderConfig | str] = {
    ProviderConfig.QWEN: ProviderConfig.GEMINI,  # qwen uses the same spec as gemini
    ProviderConfig.LLXPRT: ProviderConfig.GEMINI,  # qwen uses the same spec as gemini
}


class ConfigFormat(StrEnum):
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    TEXT = "text"
    # Special formats for encoding; not actual file formats for output
    TOON = "toon"
    ISON = "ison"


# Expected output formats per provider (if known)
PROVIDER_OUTPUT_FORMAT: dict[ProviderConfig | str, ConfigFormat] = {
    ProviderConfig.CLAUDE: ConfigFormat.JSON,
    ProviderConfig.GEMINI: ConfigFormat.JSON,
    ProviderConfig.CODEX: ConfigFormat.TOML,
    ProviderConfig.MISTRAL: ConfigFormat.TOML,
    ProviderConfig.VSCODE: ConfigFormat.JSON,
    ProviderConfig.OPENCODE: ConfigFormat.JSON,
    ProviderConfig.QWEN: ConfigFormat.JSON,
    ProviderConfig.LLXPRT: ConfigFormat.JSON,
    ProviderConfig.CRUSH: ConfigFormat.JSON,
}
