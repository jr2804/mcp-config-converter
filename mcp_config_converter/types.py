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
    QWEN = "qwen"
    LLXPRT = "llxprt"
    CRUSH = "crush"
    NCP = "ncp"


# Provider alias mapping - maps providers to their actual implementation
PROVIDER_ALIAS_MAP: dict[ProviderConfig | str, ProviderConfig | str] = {
    ProviderConfig.QWEN: ProviderConfig.GEMINI,  # qwen uses the same spec as gemini
    ProviderConfig.LLXPRT: ProviderConfig.GEMINI,  # qwen uses the same spec as gemini
    ProviderConfig.NCP: ProviderConfig.CLAUDE,  # ncp uses the same spec as claude
}


class ConfigFormat(StrEnum):
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    TOON = "toon"
    TEXT = "text"


class EncodingFormat(StrEnum):
    NONE = "none"
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
    ProviderConfig.NCP: ConfigFormat.JSON,
}
