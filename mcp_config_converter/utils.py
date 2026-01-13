"""Utility functions for MCP Config Converter."""

import os
import tempfile
from pathlib import Path
from typing import Any

import mistune
import orjson
import remarshal
import toml
import toon_format
import yaml
from mistune.renderers.markdown import MarkdownRenderer
from rich.prompt import Confirm, Prompt

from mcp_config_converter.types import PROVIDER_OUTPUT_FORMAT, ConfigFormat, ProviderConfig


def determine_config_format(cfg: str) -> ConfigFormat:
    # Empty or whitespace-only strings are TEXT, not config
    if not cfg or cfg.isspace():
        return ConfigFormat.TEXT

    # Try JSON first (strictest format)
    try:
        json_result = orjson.loads(cfg)
        # JSON strings are valid JSON but not config structures
        # Config files should be objects (dict) or arrays (list)
        if isinstance(json_result, (dict, list)):
            return ConfigFormat.JSON
    except orjson.JSONDecodeError:
        pass

    # Try TOML (also strict, always returns dict for valid TOML)
    try:
        toml.loads(cfg)
        return ConfigFormat.TOML
    except toml.TomlDecodeError:
        pass

    # Try TOON (specific format, subset of YAML-like syntax)
    try:
        toon_result = toon_format.decode(cfg)
        # TOON can parse plain text as string - config should be dict/list
        if isinstance(toon_result, (dict, list)):
            return ConfigFormat.TOON
    except toon_format.ToonDecodeError:
        pass

    # Try YAML (lenient - returns strings for plain text)
    try:
        yaml_result = yaml.safe_load(cfg)
        # YAML can parse plain text as string - config should be dict/list
        if isinstance(yaml_result, (dict, list)):
            return ConfigFormat.YAML
    except yaml.YAMLError:
        pass

    # Default to TEXT
    return ConfigFormat.TEXT


def parse_config_string(content: str) -> dict[str, Any] | list[Any] | None:
    """Parse configuration string into a Python object.

    Tries to parse as JSON, then TOML, then YAML.
    Returns None if parsing fails or result is not a container type.
    """
    if not content or content.isspace():
        return None

    # Try JSON
    try:
        json_result = orjson.loads(content)
        if isinstance(json_result, (dict, list)):
            return json_result
    except orjson.JSONDecodeError:
        pass

    # Try TOML
    try:
        toml_result = toml.loads(content)
        if isinstance(toml_result, dict):  # TOML always returns dict
            return toml_result
    except toml.TomlDecodeError:
        pass

    # Try YAML
    try:
        yaml_result = yaml.safe_load(content)
        if isinstance(yaml_result, (dict, list)):
            return yaml_result
    except yaml.YAMLError:
        pass

    return None


def get_env_variable(name: str, default: str | None = None) -> str | None:
    """Get environment variable safely.

    Args:
        name: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default
    """
    return os.getenv(name, default)


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, creating if necessary.

    Args:
        path: Directory path

    Returns:
        Path to directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Dictionary to merge on top

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def validate_file_exists(file_path: Path) -> bool:
    """Validate that a file exists.

    Args:
        file_path: Path to file

    Returns:
        True if file exists
    """
    return Path(file_path).is_file()


def get_file_extension(file_path: Path) -> str:
    """Get file extension without leading dot.

    Args:
        file_path: Path to file

    Returns:
        File extension
    """
    return Path(file_path).suffix.lstrip(".")


def clean_llm_output(output: str) -> str:
    """Clean LLM output by removing markdown code blocks and extra text.

    Args:
        output: Raw LLM output

    Returns:
        Cleaned output
    """
    # sometimes, the output is wrapped in markdown code blocks
    fmt_md = mistune.create_markdown(renderer=MarkdownRenderer())
    _, state = fmt_md.parse(output)
    for t in state.tokens:
        if t["type"] == "block_code":
            output = t["raw"].strip()
            break

    # if JSON, check if wrapped in array
    if determine_config_format(output) == ConfigFormat.JSON:
        try:
            parsed = orjson.loads(output)
            if isinstance(parsed, list) and len(parsed) == 1:
                output = orjson.dumps(parsed[0]).decode("utf-8")
        except orjson.JSONDecodeError:
            pass

    output = output.strip()
    return output


def prompt_for_choice(message: str, choices: list[str], default: str | None = None) -> str:
    """Prompt user to select from a list of choices.

    Args:
        message: Prompt message
        choices: List of valid choices
        default: Default choice if user presses enter

    Returns:
        Selected choice
    """
    res = Prompt.ask(message, choices=choices, default=default)
    return str(res) if res is not None else ""


def prompt_for_confirmation(message: str, default: bool = False) -> bool:
    """Prompt user for yes/no confirmation.

    Args:
        message: Confirmation message
        default: Default value if user presses enter

    Returns:
        True if user confirms, False otherwise
    """
    return Confirm.ask(message, default=default)


def prompt_for_text(message: str, default: str | None = None) -> str:
    """Prompt user for text input.

    Args:
        message: Prompt message
        default: Default value if user presses enter

    Returns:
        User input
    """
    res = Prompt.ask(message, default=default)
    return str(res) if res is not None else ""


def select_provider(default: str = "claude") -> str:
    """Interactive provider selection.

    Args:
        default: Default provider

    Returns:
        Selected provider
    """
    providers: list[str] = ProviderConfig.__members__.keys()  # type: ignore
    return prompt_for_choice("Select target format", choices=providers, default=default)


def select_format(default: str = "json") -> str:
    """Interactive format selection.

    Args:
        default: Default format

    Returns:
        Selected format
    """
    formats: list[str] = ConfigFormat.__members__.keys()  # type: ignore
    return prompt_for_choice("Select output format", choices=formats, default=default)


def convert_format(data: str, target_config: ProviderConfig | str) -> str:
    """Convert data string to specified format.

    Args:
        data: Input data string
        target_format: Target configuration format

    Returns:
        Converted data string
    """
    output = data
    if (expected_format := PROVIDER_OUTPUT_FORMAT.get(target_config, "text")) != "text":
        current_format = determine_config_format(data)
        if current_format != expected_format:
            # special case TOON: convert to JSON first
            if current_format == ConfigFormat.TOON and (current_format := ConfigFormat.JSON) == "json":
                data = orjson.dumps(toon_format.decode(data)).decode("utf-8")

            if expected_format in [ConfigFormat.JSON, ConfigFormat.YAML, ConfigFormat.TOML]:
                # convert supported formats
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_input_file = Path(temp_dir) / f"input.{current_format}"
                    temp_input_file.write_text(data, encoding="utf-8")
                    temp_output_file = Path(temp_dir) / f"output.{expected_format}"

                    remarshal.remarshal(str(current_format), str(expected_format), temp_input_file, temp_output_file)
                    output = temp_output_file.read_text(encoding="utf-8")
            else:
                raise ValueError(f"Cannot convert format '{current_format}' to expected format '{expected_format}' for provider '{target_config}'")

    return output
