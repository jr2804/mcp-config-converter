
from mcp_config_converter.types import ProviderConfig
from mcp_config_converter.utils import convert_format


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
