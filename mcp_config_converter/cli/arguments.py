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
InteractiveOpt = typer.Option(False, "--interactive", "-i", help="Run in interactive mode")
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
LlmProviderTypeOpt = typer.Option(
    None,
    "--llm-provider-type",
    envvar=EnvVarName.LLM_PROVIDER_TYPE,
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
PreferredProviderOpt = typer.Option(
    "auto",
    "--preferred-provider",
    "-pp",
    envvar=EnvVarName.PREFERRED_PROVIDER,
    help="Preferred LLM provider ('auto' for automatic selection, or specific provider name)",
    case_sensitive=False,
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
