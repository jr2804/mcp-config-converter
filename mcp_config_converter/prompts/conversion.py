"""MCP configuration conversion prompt templates."""

import contextlib
import importlib.resources
import json

from toon_format import encode

from mcp_config_converter.utils import parse_config_string


def _load_template(template_name: str) -> str:
    """Load a markdown template file with strict error handling."""
    try:
        template_dir = importlib.resources.files("mcp_config_converter.prompts.templates")
        template_file = template_dir.joinpath(template_name)
        if not template_file.is_file():
            raise FileNotFoundError(f"Required template file not found: {template_name}")

        content = template_file.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(f"Template file is empty: {template_name}")

        return content
    except Exception as e:
        raise RuntimeError(f"Failed to load template {template_name}: {e}")


def _get_provider_specification(target_provider: str, shift_heading_levels: int = 2) -> str:
    """Get target provider specifications."""
    try:
        spec_file = importlib.resources.files("mcp_config_converter.specs").joinpath(f"{target_provider}.md")
        content = spec_file.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(f"Specification file is empty: {target_provider}.md")

        if shift_heading_levels > 0:
            lines = content.splitlines()
            for i, line in enumerate(lines[:]):
                if line.startswith("#"):
                    lines[i] = "#" * shift_heading_levels + line

            content = "\n".join(lines)

        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Required specification file not found: {target_provider}.md")
    except Exception as e:
        raise RuntimeError(f"Failed to load template for {target_provider}: {e}")


def build_conversion_prompt(target_provider: str, input_config: str, encode_toon: bool = True) -> tuple[str, str]:
    """Build the complete conversion prompt.

    Args:
        target_provider: Target provider (claude, gemini, vscode, opencode)
        input_config: The input configuration text to process
        encode_toon: Whether to encode structured input to TOON format

    Returns:
        Complete prompt string
    """
    target_provider = target_provider.lower()
    output_format = "JSON"

    # Handle input processing
    processed_input = input_config
    if encode_toon:
        parsed_config = parse_config_string(input_config)
        if parsed_config is not None:
            with contextlib.suppress(Exception):
                processed_input = encode(parsed_config)

    # Load template
    system_prompt = _load_template("system.md")

    # Load and format main prompt template
    provider_spec = _get_provider_specification(target_provider)
    main_template = _load_template("prompt.md")

    formatted_prompt = main_template.format(
        input_config=processed_input, target_provider=target_provider, output_format=output_format, provider_spec=provider_spec
    )

    return system_prompt, formatted_prompt


def parse_conversion_output(output: str) -> str:
    """Parse output and return as formatted JSON string.

    Args:
        output: Raw LLM output string

    Returns:
        Formatted JSON string
    """
    # Output is already JSON, just validate and format it
    try:
        parsed = json.loads(output)
        return json.dumps(parsed, indent=2)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON output: {e}")
