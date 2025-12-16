"""Tests for determine_config_format function."""

import toon_format

from mcp_config_converter.types import ConfigFormat
from mcp_config_converter.utils import determine_config_format


def test_toon_format() -> None:
    """Test TOON format identification."""
    # Create a valid TOON format directly from dict
    data = {"section1": {"key1": "value1", "key2": "value2"}, "section2": {"key3": "value3"}}
    toon_config = toon_format.encode(data)
    result = determine_config_format(toon_config)
    if result != ConfigFormat.TOON:
        msg = f"Expected ConfigFormat.TOON, got {result}"
        raise AssertionError(msg)


def test_json_format() -> None:
    """Test JSON format identification."""
    json_config = '{"key1": "value1", "key2": "value2"}'
    result = determine_config_format(json_config)
    if result != ConfigFormat.JSON:
        msg = f"Expected ConfigFormat.JSON, got {result}"
        raise AssertionError(msg)


def test_yaml_format() -> None:
    """Test YAML format identification."""
    yaml_config = """- item1
- item2
"""
    result = determine_config_format(yaml_config)
    if result != ConfigFormat.YAML:
        msg = f"Expected ConfigFormat.YAML, got {result}"
        raise AssertionError(msg)


def test_toml_format() -> None:
    """Test TOML format identification."""
    toml_config = """
    [[servers]]
    [servers.alpha]
    ip = "10.0.0.1"
    """
    result = determine_config_format(toml_config)
    if result != ConfigFormat.TOML:
        msg = f"Expected ConfigFormat.TOML, got {result}"
        raise AssertionError(msg)


def test_text_format() -> None:
    """Test TEXT format identification."""
    text_config = "This is plain text with special chars @#$%^&*() and no key-value pairs and no colons and no structure and no valid yaml"
    result = determine_config_format(text_config)
    if result != ConfigFormat.TEXT:
        msg = f"Expected ConfigFormat.TEXT, got {result}"
        raise AssertionError(msg)


def test_empty_and_whitespace() -> None:
    """Test empty and whitespace-only strings are TEXT."""
    for text_config in ["", "   ", "\n", "\t\n  "]:
        result = determine_config_format(text_config)
        if result != ConfigFormat.TEXT:
            msg = f"Expected ConfigFormat.TEXT for {repr(text_config)}, got {result}"
            raise AssertionError(msg)


def test_json_array() -> None:
    """Test JSON array format identification."""
    json_config = '["item1", "item2", {"nested": "value"}]'
    result = determine_config_format(json_config)
    if result != ConfigFormat.JSON:
        msg = f"Expected ConfigFormat.JSON, got {result}"
        raise AssertionError(msg)


def test_json_string_literal() -> None:
    """Test JSON string literal is identified as TEXT (not config structure)."""
    # JSON string literal is valid JSON but not a config structure (dict/list)
    json_string = '"This is a JSON string literal"'
    result = determine_config_format(json_string)
    if result != ConfigFormat.TEXT:
        msg = f"Expected ConfigFormat.TEXT for JSON string literal, got {result}"
        raise AssertionError(msg)
