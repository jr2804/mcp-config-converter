"""Tests for configuration parsers."""

import pytest

from mcp_config_converter.models import MCPConfig
from mcp_config_converter.parsers import JSONParser, TOMLParser, YAMLParser


class TestJSONParser:
    """Tests for JSON parser."""

    def test_parse_valid_json(self) -> None:
        """Test parsing valid JSON."""
        parser = JSONParser()
        content = '{"version": "1.0", "servers": {}}'
        config = parser.parse(content)
        assert isinstance(config, MCPConfig)
        assert config.version == "1.0"

    def test_parse_bytes(self) -> None:
        """Test parsing JSON from bytes."""
        parser = JSONParser()
        content = b'{"version": "1.0", "servers": {}}'
        config = parser.parse(content)
        assert isinstance(config, MCPConfig)


class TestYAMLParser:
    """Tests for YAML parser."""

    @pytest.mark.skipif(True, reason="Requires PyYAML")
    def test_parse_valid_yaml(self) -> None:
        """Test parsing valid YAML."""
        parser = YAMLParser()
        content = 'version: "1.0"\nservers: {}'
        config = parser.parse(content)
        assert isinstance(config, MCPConfig)


class TestTOMLParser:
    """Tests for TOML parser."""

    @pytest.mark.skipif(True, reason="Requires TOML library")
    def test_parse_valid_toml(self) -> None:
        """Test parsing valid TOML."""
        parser = TOMLParser()
        content = 'version = "1.0"\n[servers]'
        config = parser.parse(content)
        assert isinstance(config, MCPConfig)
