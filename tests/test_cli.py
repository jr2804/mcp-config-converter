"""Tests for CLI functionality."""
# ruff: noqa: S101  # asserts are intended in tests

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mcp_config_converter.cli import app
from mcp_config_converter.cli.constants import SUPPORTED_PROVIDERS
from mcp_config_converter.llm.client import (
    PROVIDER_API_KEY_ENV_VARS,
    PROVIDER_DEFAULT_MODELS,
)

TEST_DATA_DIR = Path("tests/data")
TEST_INPUT_FILE = TEST_DATA_DIR / "config_vscode.json"
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
    def _has_api_key_for_provider(provider: str) -> bool:
        """Check if API key is available for a given LLM provider."""
        env_vars = PROVIDER_API_KEY_ENV_VARS.get(provider, [])
        if not env_vars:
            return True
        return any(os.getenv(var) for var in env_vars)

    @staticmethod
    def _generate_test_params() -> list:
        """Generate test parameters for all provider combinations."""
        params = []
        for output_provider in SUPPORTED_PROVIDERS:
            for llm_provider, llm_model in PROVIDER_DEFAULT_MODELS.items():
                params.append(
                    pytest.param(
                        output_provider,
                        llm_provider,
                        llm_model,
                        id=f"{output_provider}-{llm_provider}",
                    )
                )
        return params

    @staticmethod
    @pytest.mark.parametrize(
        ("output_provider", "llm_provider", "llm_model"),
        _generate_test_params(),
    )
    def test_convert_command_with_providers(
        runner: CliRunner,
        output_provider: str,
        llm_provider: str,
        llm_model: str,
    ) -> None:
        """Test convert command with all combinations of output and LLM providers.

        Makes actual LLM calls if API keys are configured. Skips tests if
        API keys are not available.
        """
        if not TestCLI._has_api_key_for_provider(llm_provider):
            pytest.skip(f"API key not configured for LLM provider: {llm_provider}")

        llm_output_dir = TEST_OUTPUT_ROOT / llm_provider
        llm_output_dir.mkdir(parents=True, exist_ok=True)
        output_file = llm_output_dir / f"{output_provider}_output.json"

        result = runner.invoke(
            app,
            [
                "convert",
                str(TEST_INPUT_FILE),
                "-p",
                output_provider,
                "-o",
                str(output_file),
                "--llm-provider-type",
                llm_provider,
                "--llm-model",
                f"{llm_provider}/{llm_model}",
                "--output-action",
                "overwrite",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

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
