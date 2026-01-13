# ruff: noqa: S101  # asserts are intended in tests
import json

from mcp_config_converter.types import ConfigFormat, ProviderConfig
from mcp_config_converter.utils import convert_format, convert_from_json, determine_config_format, parse_config_string


def test_convert_format_json_to_json_pretty() -> None:
    """Test converting JSON to JSON produces pretty-printed output."""
    raw_json = '{"key": "value", "list": [1, 2]}'
    # Claude expects JSON
    result = convert_format(raw_json, ProviderConfig.CLAUDE)

    # Check for indentation (4 spaces default)
    assert '    "key": "value"' in result
    assert '    "list": [' in result
    assert result.strip().startswith("{")
    assert result.strip().endswith("}")


def test_convert_format_toml_to_json() -> None:
    """Test converting TOML to JSON."""
    toml_data = 'key = "value"\n[section]\nsub = 1'
    # Claude expects JSON
    result = convert_format(toml_data, ProviderConfig.CLAUDE)

    assert '    "key": "value"' in result
    assert '"section": {' in result
    assert '"sub": 1' in result


def test_convert_format_yaml_to_toml() -> None:
    """Test converting YAML to TOML."""
    yaml_data = "key: value\nsection:\n  sub: 1"
    # Mistral expects TOML
    result = convert_format(yaml_data, ProviderConfig.MISTRAL)

    # TOML format check
    assert 'key = "value"' in result
    assert "[section]" in result
    assert "sub = 1" in result


def test_convert_format_invalid_json_fallback() -> None:
    """Test that invalid JSON returns original data (or handles error gracefully)."""
    # Use a string that is invalid in JSON, YAML and TOML.
    # Unclosed structure with special chars often fails YAML too.
    invalid_input = '{"key": "value", @#$%'

    result = convert_format(invalid_input, ProviderConfig.CLAUDE)
    assert result == invalid_input


def test_convert_format_text_noop() -> None:
    """Test that text format remains text if target is text (default)."""
    text = "Some random text"
    # Unknown provider defaults to text
    result = convert_format(text, "unknown_provider")
    assert result == text


def test_convert_format_json_to_yaml_to_json_roundtrip() -> None:
    """Test JSON -> YAML -> JSON roundtrip conversion preserves content using direct conversion utilities."""
    # Complex JSON data with nested structures
    original_json_data = {
        "name": "test-config",
        "version": "1.0.0",
        "servers": [
            {"name": "server1", "url": "https://api.example.com", "config": {"timeout": 30, "retries": 3, "enabled": True}},
            {"name": "server2", "url": "https://backup.example.com", "config": {"timeout": 60, "retries": 5, "enabled": False}},
        ],
        "settings": {"debug": True, "log_level": "info", "features": ["auth", "cache", "metrics"]},
    }

    # Convert to JSON string
    json.dumps(original_json_data, indent=2)

    # Since no providers expect YAML, we'll use direct conversion utilities
    # Convert JSON to YAML using direct conversion
    yaml_result = convert_from_json(original_json_data, ConfigFormat.YAML)

    # Verify it's actually YAML format
    assert determine_config_format(yaml_result) == ConfigFormat.YAML

    # Parse YAML back to Python object
    yaml_parsed = parse_config_string(yaml_result)
    assert yaml_parsed is not None
    assert isinstance(yaml_parsed, dict)

    # Convert YAML back to JSON using direct conversion
    json_roundtrip = convert_from_json(yaml_parsed, ConfigFormat.JSON)

    # Verify final result is JSON
    assert determine_config_format(json_roundtrip) == ConfigFormat.JSON

    # Parse final JSON and compare content with original
    final_parsed = parse_config_string(json_roundtrip)
    assert final_parsed is not None
    assert isinstance(final_parsed, dict)

    # Content-wise comparison (ignoring formatting differences)
    assert final_parsed["name"] == original_json_data["name"]
    assert final_parsed["version"] == original_json_data["version"]
    assert len(final_parsed["servers"]) == len(original_json_data["servers"])
    assert final_parsed["servers"][0]["name"] == original_json_data["servers"][0]["name"]
    assert final_parsed["servers"][0]["config"]["timeout"] == original_json_data["servers"][0]["config"]["timeout"]
    assert final_parsed["settings"]["debug"] == original_json_data["settings"]["debug"]
    assert final_parsed["settings"]["features"] == original_json_data["settings"]["features"]


def test_convert_format_json_to_toml_to_json_roundtrip() -> None:
    """Test JSON -> TOML -> JSON roundtrip conversion preserves content."""
    # TOML-compatible JSON data (TOML has some restrictions)
    original_json_data = {
        "title": "TOML Example",
        "owner": {"name": "Tom Preston-Werner", "organization": "GitHub"},
        "database": {"server": "192.168.1.1", "ports": [8001, 8002, 8003], "connection_max": 5000, "enabled": True},
        "servers": {"alpha": {"ip": "10.0.0.1", "dc": "eqdc10"}, "beta": {"ip": "10.0.0.2", "dc": "eqdc10", "country": "China"}},
    }

    # Convert to JSON string
    json_str = json.dumps(original_json_data, indent=2)

    # Convert JSON to TOML
    toml_result = convert_format(json_str, ProviderConfig.MISTRAL)  # Mistral expects TOML

    # Verify it's actually TOML format
    assert determine_config_format(toml_result) == ConfigFormat.TOML

    # Parse TOML back to Python object
    toml_parsed = parse_config_string(toml_result)
    assert toml_parsed is not None

    # Convert TOML back to JSON
    json_roundtrip = convert_format(toml_result, ProviderConfig.CLAUDE)  # Claude expects JSON

    # Verify final result is JSON
    assert determine_config_format(json_roundtrip) == ConfigFormat.JSON

    # Parse final JSON and compare content with original
    final_parsed = parse_config_string(json_roundtrip)
    assert final_parsed is not None

    # Content-wise comparison (ignoring formatting differences)
    assert final_parsed["title"] == original_json_data["title"]
    assert final_parsed["owner"]["name"] == original_json_data["owner"]["name"]
    assert final_parsed["database"]["server"] == original_json_data["database"]["server"]
    assert final_parsed["database"]["ports"] == original_json_data["database"]["ports"]
    assert final_parsed["database"]["connection_max"] == original_json_data["database"]["connection_max"]
    assert final_parsed["database"]["enabled"] == original_json_data["database"]["enabled"]
    assert final_parsed["servers"]["alpha"]["ip"] == original_json_data["servers"]["alpha"]["ip"]
    assert final_parsed["servers"]["beta"]["country"] == original_json_data["servers"]["beta"]["country"]
