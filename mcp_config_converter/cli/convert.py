from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from mcp_config_converter.cli import app, arguments
from mcp_config_converter.cli.constants import SUPPORTED_PROVIDERS, VALID_OUTPUT_ACTIONS, get_default_output_path
from mcp_config_converter.cli.utils import (
    console,
    validate_format_choice,
    validate_output_action,
)
from mcp_config_converter.llm import LiteLLMClient, create_client_from_env
from mcp_config_converter.llm.client import PROVIDER_DEFAULT_MODELS
from mcp_config_converter.transformers import ConfigTransformer


def _parse_model_arg(model_arg: str | None) -> str | int | None:
    """Parse model argument, converting numeric strings to integers.

    Args:
        model_arg: Model argument from CLI (string or None)

    Returns:
        Integer if the string represents a valid integer, otherwise the original string or None
    """
    if model_arg is None:
        return None

    # Try to parse as integer
    try:
        return int(model_arg)
    except ValueError:
        # Not a number, return as string
        return model_arg


@app.command(name="convert")
def convert(
    ctx: typer.Context,
    input_file: Path | None = arguments.InputFileArg,
    output: Path | None = arguments.OutputOpt,
    provider: str | None = arguments.ProviderOpt,
    output_action: str = arguments.OutputActionOpt,
    input_content: str | None = arguments.InputContentOpt,
    encode_toon: bool = arguments.EncodeToonOpt,
    llm_base_url: str | None = arguments.LlmBaseUrlOpt,
    llm_provider: str | None = arguments.LlmProviderOpt,
    llm_api_key: str | None = arguments.LlmApiKeyOpt,
    llm_model: str | None = arguments.LlmModelOpt,
    cache_dir: str | None = arguments.CacheDirOpt,
    enable_cache: bool = arguments.EnableCacheOpt,
    verbose: bool = arguments.VerboseOpt,
    version: Annotated[bool | None, arguments.VersionOpt] = None,
) -> None:
    """Convert an MCP configuration file to a supported format using LLM.

    Args:
        ctx: Typer context
        input_file: Input file path
        output: Output file path
        provider: Target provider format (claude, gemini, vscode, opencode)
        output_action: Action when output file exists
        input_content: Raw input configuration content
        encode_toon: Whether to encode JSON input to TOON format
        llm_base_url: Custom base URL for LLM provider
        llm_provider: LLM provider type
        llm_api_key: API key for LLM provider
        llm_model: Model name or index for LLM provider
        cache_dir: Custom directory for disk cache
        enable_cache: Enable disk caching for LLM API calls
        verbose: Verbose output
        version: Show version and exit
    """
    try:
        # Validate input source
        if input_file is None and input_content is None:
            console.print("[red]Error: Either input file or --input-content must be provided[/red]")
            raise typer.Exit(1)

        # Handle input source (file or content)
        if input_content is not None:
            # Using raw content input
            actual_input_file = None
        else:
            # Using file input
            actual_input_file = input_file
            input_content = None



        if provider and not validate_format_choice(provider):
            valid_formats = ", ".join(SUPPORTED_PROVIDERS)
            console.print(f"[red]Error:[/red] Invalid provider '{provider}'. Choose from: {valid_formats}")
            raise typer.Exit(1)

        if not validate_output_action(output_action):
            valid_actions = ", ".join(VALID_OUTPUT_ACTIONS)
            console.print(f"[red]Error:[/red] Invalid output action. Choose from: {valid_actions}")
            raise typer.Exit(1)

        if not output and provider:
            default_suffix = input_file.with_suffix(".mcp.json") if input_file else Path("input.mcp.json")
            output = get_default_output_path(provider)[0] if provider else default_suffix

        input_desc = actual_input_file.name if actual_input_file else "raw input"
        console.print(f"[blue]Converting {input_desc}...[/blue]")

        try:
            # Create LiteLLM client instance
            if llm_provider:
                # Explicit provider specified - create client with provided/default parameters
                # Parse model argument - convert numeric strings to integers for index-based selection
                parsed_model = _parse_model_arg(llm_model)
                model = parsed_model if parsed_model is not None else PROVIDER_DEFAULT_MODELS.get(llm_provider, "gpt-4o-mini")

                # Build optional kwargs
                optional_kwargs = {}
                if llm_api_key:
                    optional_kwargs["api_key"] = llm_api_key
                if llm_base_url:
                    optional_kwargs["base_url"] = llm_base_url
                if cache_dir:
                    optional_kwargs["cache_dir"] = cache_dir
                if enable_cache:
                    optional_kwargs["enable_cache"] = enable_cache

                llm_client = LiteLLMClient(provider=llm_provider, model=model, **optional_kwargs)
            else:
                # Auto-detect from environment
                llm_client = create_client_from_env()
                if llm_client is None:
                    console.print("[red]Error: No LLM provider configured. Please set API keys or use --llm-api-key[/red]")
                    raise typer.Exit(1)

            # Create transformer instance
            transformer = ConfigTransformer(llm_client=llm_client, encode_toon=encode_toon)

            if provider:
                # Perform conversion
                result = transformer.transform_file(actual_input_file, provider) if actual_input_file else transformer.transform(input_content or "", provider)

                # Handle output file actions
                if output and output.exists():
                    match output_action.lower():
                        case "skip":
                            console.print(f"[yellow]Skipping conversion: output file {output} already exists (action: skip)[/yellow]")
                            return
                        case "merge":
                            console.print(f"[blue]Merging with existing file: {output} (action: merge)[/blue]")

                            existing_data = json.loads(output.read_text(encoding="utf-8"))
                            new_data = json.loads(result)
                            existing_data.update(new_data)
                            result = json.dumps(existing_data, indent=2)
                        case _:
                            console.print(f"[blue]Will overwrite existing file: {output} (action: overwrite)[/blue]")

                # Write output file if specified
                if output:
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(result, encoding="utf-8")

                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target provider: [cyan]{provider}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")
                    if verbose:
                        console.print("\n[bold blue]Converted Configuration:[/bold blue]")
                        console.print(result)
                else:
                    console.print(f"[green]SUCCESS[/green] Input file: [cyan]{actual_input_file or 'raw input'}[/cyan]")
                    console.print(f"[green]SUCCESS[/green] Target provider: [cyan]{provider}[/cyan]")
                    console.print("[green]SUCCESS[/green] Output: [green]No output file specified (result generated)[/green]")
                    console.print("\n[bold blue]Converted Configuration:[/bold blue]")
                    console.print(result)
            else:
                console.print(f"[green]SUCCESS[/green] Input file: [cyan]{input_file}[/cyan]")
                if provider:
                    console.print(f"[green]SUCCESS[/green] Target provider: [cyan]{provider}[/cyan]")
                if output:
                    console.print(f"[green]SUCCESS[/green] Output file: [green]{output}[/green]")

        except Exception as exc:
            console.print(f"[red]Error during conversion:[/red] {str(exc)}")
            raise typer.Exit(1)

        console.print("\n[bold green]SUCCESS Conversion completed successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Conversion cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as exc:
        console.print(f"\n[red]Error:[/red] {str(exc)}")
        raise typer.Exit(1)
