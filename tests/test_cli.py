"""Tests for CLI functionality."""

import pytest
from typer.testing import CliRunner

from mcp_config_converter.cli import app


@pytest.fixture
def runner() -> CliRunner:
    """Create a Typer CLI test runner."""
    return CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    @staticmethod
    def test_cli_help(runner: CliRunner) -> None:
        """Test CLI help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "MCP Config Converter" in result.stdout

        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "mcp-config-converter v" in result.stdout

    @staticmethod
    def test_convert_command_opencode(runner: CliRunner) -> None:
        """Test convert command for opencode provider."""
        result = runner.invoke(app, ["convert", "data/input.json", "-p", "opencode", "-pp", "auto"])
        assert result.exit_code == 0

    @staticmethod
    def test_convert_command_claude(runner: CliRunner) -> None:
        """Test convert command for claude provider."""
        result = runner.invoke(app, ["convert", "tests/data/input.json", "-p", "claude", "-pp", "auto"])
        assert result.exit_code == 0

    @staticmethod
    def test_convert_command_gemini(runner: CliRunner) -> None:
        """Test convert command for gemini provider."""
        result = runner.invoke(app, ["convert", "data/input.json", "-p", "gemini", "-pp", "auto"])
        assert result.exit_code == 0

    @staticmethod
    def test_convert_command_codex(runner: CliRunner) -> None:
        """Test convert command for codex provider."""
        result = runner.invoke(app, ["convert", "data/input.json", "-p", "codex", "-pp", "auto"])
        assert result.exit_code == 0

    @staticmethod
    def test_convert_command_mistral(runner: CliRunner) -> None:
        """Test convert command for mistral provider."""
        result = runner.invoke(app, ["convert", "data/input.json", "-p", "mistral", "-pp", "auto"])
        assert result.exit_code == 0

    @staticmethod
    def test_convert_command_vscode(runner: CliRunner) -> None:
        """Test convert command for vscode provider."""
        result = runner.invoke(app, ["convert", "data/input.json", "-p", "vscode", "-pp", "auto"])
        assert result.exit_code == 0

    @staticmethod
    def test_validate_command(runner: CliRunner) -> None:
        """Test validate command."""
        result = runner.invoke(app, ["validate", "data/config.json"])
        assert result.exit_code == 0

    @staticmethod
    def test_llm_check_command(runner: CliRunner) -> None:
        """Test llm-check command."""
        result = runner.invoke(app, ["llm-check"])
        assert result.exit_code == 0
