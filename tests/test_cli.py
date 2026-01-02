"""Tests for CLI functionality."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from mcp_config_converter import transformers
from mcp_config_converter.cli import app
from mcp_config_converter.cli.constants import PROVIDER_DEFAULT_OUTPUT_FILES

TEST_OUTPUT_ROOT = Path("tests/temp")


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
        result = runner.invoke(
            app,
            [
                "convert",
                "data/input.json",
                "-p",
                "opencode",
                "-pp",
                "auto",
                "--llm-provider-type",
                "ollama",
                "--llm-model",
                "ollama/llama2",
            ],
        )
        assert result.exit_code == 0

    @staticmethod
    def test_convert_command_claude(runner: CliRunner) -> None:
        """Test convert command for claude provider."""
        result = runner.invoke(
            app,
            [
                "convert",
                "tests/data/input.json",
                "-p",
                "claude",
                "-pp",
                "auto",
                "--llm-provider-type",
                "ollama",
                "--llm-model",
                "ollama/llama2",
            ],
        )
        assert result.exit_code == 0

    @staticmethod
    def test_convert_command_gemini(runner: CliRunner) -> None:
        """Test convert command for gemini provider."""
        result = runner.invoke(
            app,
            [
                "convert",
                "data/input.json",
                "-p",
                "gemini",
                "-pp",
                "auto",
                "--llm-provider-type",
                "ollama",
                "--llm-model",
                "ollama/llama2",
            ],
        )
        assert result.exit_code == 0

    @staticmethod
    def test_convert_command_codex(runner: CliRunner) -> None:
        """Test convert command for codex provider."""
        result = runner.invoke(
            app,
            [
                "convert",
                "data/input.json",
                "-p",
                "codex",
                "-pp",
                "auto",
                "--llm-provider-type",
                "ollama",
                "--llm-model",
                "ollama/llama2",
            ],
        )
        assert result.exit_code == 0

    @staticmethod
    def test_convert_command_mistral(runner: CliRunner) -> None:
        """Test convert command for mistral provider."""
        result = runner.invoke(
            app,
            [
                "convert",
                "data/input.json",
                "-p",
                "mistral",
                "-pp",
                "auto",
                "--llm-provider-type",
                "ollama",
                "--llm-model",
                "ollama/llama2",
            ],
        )
        assert result.exit_code == 0

    @staticmethod
    def test_convert_command_vscode(runner: CliRunner) -> None:
        """Test convert command for vscode provider."""
        result = runner.invoke(
            app,
            [
                "convert",
                "data/input.json",
                "-p",
                "vscode",
                "-pp",
                "auto",
                "--llm-provider-type",
                "ollama",
                "--llm-model",
                "ollama/llama2",
            ],
        )
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

    @staticmethod
    @pytest.fixture(autouse=True)
    def _clear_llm_env(monkeypatch: pytest.MonkeyPatch) -> None:
        """Clear provider env vars so tests don't pick up host credentials."""
        for key in [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "GOOGLE_GENERATIVE_AI_API_KEY",
            "MISTRAL_API_KEY",
            "DEEPSEEK_API_KEY",
            "PERPLEXITY_API_KEY",
            "OPENROUTER_API_KEY",
            "SAMBANOVA_API_KEY",
            "ZAI_API_KEY",
            "VERTEX_AI_PROJECT",
            "GOOGLE_APPLICATION_CREDENTIALS",
        ]:
            monkeypatch.delenv(key, raising=False)

        # Stub out LLM-based transformations to avoid network calls
        monkeypatch.setattr(transformers.ConfigTransformer, "transform", lambda self, *_args, **_kwargs: "{}")
        monkeypatch.setattr(transformers.ConfigTransformer, "transform_file", lambda self, *_args, **_kwargs: "{}")

        # Redirect output files into tests/data to avoid clobbering real project files
        test_root = TEST_OUTPUT_ROOT
        monkeypatch.setitem(PROVIDER_DEFAULT_OUTPUT_FILES, "opencode", test_root / ".opencode" / "settings.json")
        monkeypatch.setitem(PROVIDER_DEFAULT_OUTPUT_FILES, "claude", test_root / ".claude" / "mcp.json")
        monkeypatch.setitem(PROVIDER_DEFAULT_OUTPUT_FILES, "gemini", test_root / ".gemini" / "mcp.json")
        monkeypatch.setitem(PROVIDER_DEFAULT_OUTPUT_FILES, "codex", test_root / ".mcp.json")
        monkeypatch.setitem(PROVIDER_DEFAULT_OUTPUT_FILES, "mistral", test_root / ".vibe" / "config.toml")
        monkeypatch.setitem(PROVIDER_DEFAULT_OUTPUT_FILES, "vscode", test_root / ".vscode" / "mcp.json")
