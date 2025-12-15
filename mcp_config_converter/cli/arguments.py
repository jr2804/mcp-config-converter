from __future__ import annotations

from pathlib import Path

import typer


def input_file_argument() -> Path:
    return typer.Argument(
        ...,
        help="Input configuration file path",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    )


def config_file_argument() -> Path:
    return typer.Argument(
        ...,
        help="Configuration file to validate",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    )


def output_option() -> Path | None:
    return typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path",
    )


def format_option() -> str | None:
    return typer.Option(
        None,
        "--format",
        "-f",
        help="Output format (provider type: github-copilot-cli, vscode, gemini, claude, codex, opencode)",
    )


def interactive_option() -> bool:
    return typer.Option(
        False,
        "--interactive",
        "-i",
        help="Run in interactive mode",
    )


def output_action_option() -> str:
    return typer.Option(
        "overwrite",
        "--output-action",
        "-a",
        help="Action when output file exists: overwrite, skip, or merge",
        case_sensitive=False,
    )


def llm_base_url_option() -> str | None:
    return typer.Option(
        None,
        "--llm-base-url",
        help="Custom base URL for LLM provider (for OpenAI/Anthropic compatible APIs)",
    )


def llm_provider_type_option() -> str | None:
    return typer.Option(
        None,
        "--llm-provider-type",
        help="LLM provider type: 'openai' or 'anthropic' for custom providers",
    )


def llm_api_key_option() -> str | None:
    return typer.Option(
        None,
        "--llm-api-key",
        help="API key for LLM provider (overrides environment variables)",
    )


def llm_model_option() -> str | None:
    return typer.Option(
        None,
        "--llm-model",
        help="Model name for the configured LLM provider",
    )


def preferred_provider_option() -> str:
    return typer.Option(
        "auto",
        "--preferred-provider",
        "-pp",
        help="Preferred LLM provider ('auto' for automatic selection, or specific provider name)",
        case_sensitive=False,
    )


def input_content_option() -> str | None:
    return typer.Option(
        None,
        "--input-content",
        "-c",
        help="Raw input configuration content (alternative to input file)",
    )


def encode_toon_option() -> bool:
    return typer.Option(
        True,
        "--encode-toon/--no-encode-toon",
        help="Encode JSON input to TOON format for LLM processing",
    )


def decode_toon_option() -> bool:
    return typer.Option(
        True,
        "--decode-toon/--no-decode-toon",
        help="Decode TOON output from LLM back to JSON format",
    )
