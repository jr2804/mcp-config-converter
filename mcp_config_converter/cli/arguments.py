from __future__ import annotations

import typer

from mcp_config_converter._version import version as _version
from mcp_config_converter.cli import console
from mcp_config_converter.cli.constants import SUPPORTED_PROVIDERS, VALID_OUTPUT_ACTIONS, EnvVarName, RichHelpPanel


def version_callback(value: bool = True) -> None:
    """Print version and exit."""
    if value:
        console.print(f"mcp-config-converter v{_version}")
        raise typer.Exit()


# Argument definitions
InputFileArg = typer.Argument(None, help="Input configuration file path")
ConfigFileArg = typer.Argument(None, help="Configuration file to validate")

# Option definitions
OutputOpt = typer.Option(None, "--output", "-o", help="Output file path")
ProviderOpt = typer.Option(None, "--provider", "-p", help=f"Target provider format ({', '.join(SUPPORTED_PROVIDERS)})")

OutputActionOpt = typer.Option(
    "overwrite",
    "--output-action",
    "-a",
    help=f"Action when output file exists: {', '.join(VALID_OUTPUT_ACTIONS)}",
    case_sensitive=False,
)

# Common options with rich_help_panel grouping
VerboseOpt = typer.Option(False, "--verbose", help="Verbose output", rich_help_panel=RichHelpPanel.OTHER)
VersionOpt = typer.Option(
    "--version",
    callback=version_callback,
    is_eager=True,  # help="Show version and exit.", rich_help_panel=RichHelpPanel.OTHER
)

# LLM-specific options
LlmBaseUrlOpt = typer.Option(
    None,
    "--llm-base-url",
    envvar=EnvVarName.LLM_BASE_URL,
    help="Custom base URL for LLM provider (for OpenAI/Anthropic compatible APIs)",
    rich_help_panel=RichHelpPanel.LLM,
)
LlmProviderOpt = typer.Option(
    None,
    "--llm-provider",
    "-lp",
    envvar=EnvVarName.LLM_PROVIDER,
    help="LLM provider type: e.g., 'openai', 'anthropic', 'zai'",
    rich_help_panel=RichHelpPanel.LLM,
)
LlmApiKeyOpt = typer.Option(
    None,
    "--llm-api-key",
    envvar=EnvVarName.LLM_API_KEY,
    help="API key for LLM provider (overrides provider-specific env vars)",
    rich_help_panel=RichHelpPanel.LLM,
)
LlmModelOpt = typer.Option(
    None,
    "--llm-model",
    "-lm",
    envvar=EnvVarName.LLM_MODEL,
    help="Model name or index (e.g., 'gpt-4o-mini' or 0 for first model, -1 for last)",
    rich_help_panel=RichHelpPanel.LLM,
)
NoAuthCheckOpt = typer.Option(
    False,
    "--no-auth-check",
    help="Skip API key authentication check (faster)",
    rich_help_panel=RichHelpPanel.LLM,
)
EnableCacheOpt = typer.Option(
    False,
    "--enable-cache",
    "-ec",
    envvar=EnvVarName.LLM_CACHE_ENABLED,
    help="Enable disk caching for LLM API calls to reduce costs and latency",
    rich_help_panel=RichHelpPanel.LLM,
)
CacheDirOpt = typer.Option(
    None,
    "--cache-dir",
    help="Custom directory for disk cache (default: LiteLLM's default)",
    rich_help_panel=RichHelpPanel.LLM,
)
CheckProviderEndpointOpt = typer.Option(
    False,
    "--check-provider-endpoint",
    help="Query provider endpoints for accurate model lists (slower but more accurate)",
    envvar=EnvVarName.LLM_CHECK_PROVIDER_ENDPOINT,
    rich_help_panel=RichHelpPanel.LLM,
)

# Conversion-specific options
InputContentOpt = typer.Option(
    None,
    "--input-content",
    "-c",
    help="Raw input configuration content (alternative to input file)",
)
EncodeToonOpt = typer.Option(
    True,
    "--encode-toon/--no-encode-toon",
    help="Encode JSON input to TOON format for LLM processing",
)
