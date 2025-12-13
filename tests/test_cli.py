"""Tests for CLI functionality."""

import pytest
from click.testing import CliRunner

from mcp_config_converter.cli import cli


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_cli_help(self, runner):
        """Test CLI help output."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "MCP Config Converter" in result.output

    def test_cli_version(self, runner):
        """Test CLI version output."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0

    @pytest.mark.skip(reason="Requires test file")
    def test_convert_command(self, runner):
        """Test convert command."""
        result = runner.invoke(cli, ['convert', 'input.json'])
        assert result.exit_code == 0

    @pytest.mark.skip(reason="Requires test file")
    def test_validate_command(self, runner):
        """Test validate command."""
        result = runner.invoke(cli, ['validate', 'config.json'])
        assert result.exit_code == 0

    def test_init_command(self, runner):
        """Test init command."""
        result = runner.invoke(cli, ['init'])
        assert result.exit_code == 0
        assert "Initializing" in result.output
