"""Tests for configuration formatters."""

import pytest
import json

from mcp_config_converter.models import MCPConfig, MCPServer
from mcp_config_converter.formatters import (
    ClaudeFormatter,
    GeminiFormatter,
    VSCodeFormatter,
    OpenCodeFormatter,
)


@pytest.fixture
def sample_config():
    """Create a sample MCP configuration."""
    return MCPConfig(
        version="1.0",
        servers={
            "example": MCPServer(
                name="Example Server",
                command="python",
                args=["-m", "example"],
                env={"DEBUG": "true"},
            )
        },
    )


class TestClaudeFormatter:
    """Tests for Claude formatter."""

    def test_format_dict(self, sample_config):
        """Test formatting to dictionary."""
        formatter = ClaudeFormatter()
        result = formatter.format_dict(sample_config)
        assert "version" in result
        assert "tools" in result
        assert "example" in result["tools"]

    def test_format_string(self, sample_config):
        """Test formatting to JSON string."""
        formatter = ClaudeFormatter()
        result = formatter.format(sample_config)
        parsed = json.loads(result)
        assert "version" in parsed
        assert "tools" in parsed


class TestGeminiFormatter:
    """Tests for Gemini formatter."""

    def test_format_dict(self, sample_config):
        """Test formatting to dictionary."""
        formatter = GeminiFormatter()
        result = formatter.format_dict(sample_config)
        assert "schemaVersion" in result
        assert "models" in result
        assert "example" in result["models"]


class TestVSCodeFormatter:
    """Tests for VS Code formatter."""

    def test_format_dict(self, sample_config):
        """Test formatting to dictionary."""
        formatter = VSCodeFormatter()
        result = formatter.format_dict(sample_config)
        assert "[mcp-servers]" in result
        assert "example" in result["[mcp-servers]"]


class TestOpenCodeFormatter:
    """Tests for OpenCode formatter."""

    def test_format_dict(self, sample_config):
        """Test formatting to dictionary."""
        formatter = OpenCodeFormatter()
        result = formatter.format_dict(sample_config)
        assert "format_version" in result
        assert "mcp_servers" in result
        assert "example" in result["mcp_servers"]
