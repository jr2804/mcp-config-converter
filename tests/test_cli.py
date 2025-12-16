"""Tests for CLI functionality."""

import pytest
from typer.testing import CliRunner

from mcp_config_converter.cli.main import app


@pytest.fixture
def runner():
    """Create a Typer CLI test runner."""
    return CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_cli_help(self, runner) -> None:
        """Test CLI help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "MCP Config Converter" in result.stdout

        result = runner.invoke(app, ["--version"])
        assert "0.1.0" in result.stdout

    @pytest.mark.skip(reason="Requires test file")
    def test_convert_command(self, runner) -> None:
        """Test convert command."""
        result = runner.invoke(app, ["convert", "input.json"])
        assert result.exit_code == 0

    @pytest.mark.skip(reason="Requires test file")
    def test_validate_command(self, runner) -> None:
        """Test validate command."""
        result = runner.invoke(app, ["validate", "config.json"])
        assert result.exit_code == 0

    def test_init_command(self, runner, monkeypatch) -> None:
        """Test init command."""
        # Mock configure_llm_provider to avoid needing actual API keys
        monkeypatch.setattr("mcp_config_converter.cli.init.configure_llm_provider", lambda ctx, verbose=False: None)

        # Default mode is non-interactive, no flag needed
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert "initialized" in result.stdout.lower()
