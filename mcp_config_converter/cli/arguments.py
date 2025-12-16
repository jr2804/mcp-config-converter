from __future__ import annotations

import typer

from .constants import SUPPORTED_PROVIDERS, VALID_OUTPUT_ACTIONS

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
InitProviderOpt = typer.Option(None, "--provider", "-p", help=f"Target provider type for initialization ({', '.join(SUPPORTED_PROVIDERS)})")

# Common options with rich_help_panel grouping
VerboseOpt = typer.Option(False, "--verbose", help="Verbose output", rich_help_panel="Other Options")

# LLM-specific options
LlmBaseUrlOpt = typer.Option(
    None,
    "--llm-base-url",
    help="Custom base URL for LLM provider (for OpenAI/Anthropic compatible APIs)",
    rich_help_panel="LLM Parameters",
)
LlmProviderTypeOpt = typer.Option(
    None,
    "--llm-provider-type",
    help="LLM provider type: 'openai' or 'anthropic' for custom providers",
    rich_help_panel="LLM Parameters",
)
LlmApiKeyOpt = typer.Option(
    None,
    "--llm-api-key",
    help="API key for LLM provider (overrides environment variables)",
    rich_help_panel="LLM Parameters",
)
LlmModelOpt = typer.Option(
    None,
    "--llm-model",
    help="Model name for the configured LLM provider",
    rich_help_panel="LLM Parameters",
)
PreferredProviderOpt = typer.Option(
    "auto",
    "--preferred-provider",
    "-pp",
    help="Preferred LLM provider ('auto' for automatic selection, or specific provider name)",
    case_sensitive=False,
    rich_help_panel="LLM Parameters",
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
DecodeToonOpt = typer.Option(
    True,
    "--decode-toon/--no-decode-toon",
    help="Decode TOON output from LLM back to JSON format",
)
