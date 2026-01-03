"""Tests for CLI functionality."""
# ruff: noqa: S101  # asserts are intended in tests

import json
import os
from pathlib import Path

import pytest
import toml
from typer.testing import CliRunner

from mcp_config_converter.cli import app
from mcp_config_converter.cli.constants import SUPPORTED_PROVIDERS
from mcp_config_converter.llm.client import (
    PROVIDER_API_KEY_ENV_VARS,
    PROVIDER_DEFAULT_MODELS,
)
from mcp_config_converter.types import PROVIDER_OUTPUT_FORMAT, ConfigFormat

TEST_DATA_DIR = Path("tests/data")
TEST_INPUT_FILE = TEST_DATA_DIR / "config_vscode.json"
TEST_OUTPUT_ROOT = Path("tests/temp")


@pytest.fixture
def runner() -> CliRunner:
    """Create a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def expected_server_data() -> tuple[int, set[str]]:
    """Parse test input file and return expected server count and names."""
    input_data = json.loads(TEST_INPUT_FILE.read_text(encoding="utf-8"))

    # VS Code format uses "servers" key
    servers_dict = input_data.get("servers", {})
    server_count = len(servers_dict)
    server_names = {server.lower() for server in servers_dict}

    return server_count, server_names


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
    @pytest.mark.parametrize(
        ("output_provider", "llm_provider", "llm_model"),
        _generate_test_params(),
    )
    def test_convert_command_with_providers(
        runner: CliRunner,
        output_provider: str,
        llm_provider: str,
        llm_model: str,
        expected_server_data: tuple[int, set[str]],
    ) -> None:
        """Test convert command with all combinations of output and LLM providers.

        Makes actual LLM calls if API keys are configured. Skips tests if
        API keys are not available. VS Code to VS Code conversions are skipped.
        """
        # Skip vscode-to-vscode conversions (no conversion needed)
        if output_provider == "vscode":
            pytest.skip("VS Code to VS Code conversion is not applicable")

        if not TestCLI._has_api_key_for_provider(llm_provider):
            pytest.skip(f"API key not configured for LLM provider: {llm_provider}")

        expected_count, expected_names = expected_server_data

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

        server_count = TestCLI._count_servers_in_output(output_file, output_provider)
        assert server_count == expected_count, f"Expected {expected_count} servers in output, but found {server_count} for provider {output_provider}"

        assert TestCLI._verify_server_names(output_file, output_provider, expected_names), f"Server name verification failed for provider {output_provider}"

        # TODO: Add stricter schema-based validation in future
        # - Validate against provider-specific JSON schema
        # - Check required fields per server type (stdio, http, sse)
        # - Validate environment variable expansions
        # - Check for provider-specific constraints (e.g., timeout values)

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
    def test_show_defaults_command(runner: CliRunner) -> None:
        """Test show-defaults command."""
        result = runner.invoke(app, ["show-defaults"])
        assert result.exit_code == 0
        assert "Default Output Paths" in result.stdout
        assert "qwen" in result.stdout
        assert ".qwen/settings.json" in result.stdout
        assert "gemini" in result.stdout

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
    def _count_servers_in_output(output_file: Path, output_provider: str) -> int:
        """Count number of MCP servers in output configuration file.

        Args:
            output_file: Path to generated output file
            output_provider: The output provider name (to determine format)

        Returns:
            Number of servers found in output
        """
        content = output_file.read_text(encoding="utf-8")
        output_format = PROVIDER_OUTPUT_FORMAT.get(output_provider)

        if output_format == ConfigFormat.JSON:
            data = json.loads(content)
            for key in ["mcpServers", "servers", "mcp"]:
                if key in data and isinstance(data[key], dict):
                    return len(data[key])
            return 0

        elif output_format == ConfigFormat.TOML:
            data = toml.loads(content)
            if "mcp_servers" in data:
                servers = data["mcp_servers"]
                if isinstance(servers, (dict, list)):
                    return len(servers)
            return 0

        else:
            return 0

    @staticmethod
    def _verify_server_names(output_file: Path, output_provider: str, expected_server_names: set[str]) -> bool:
        """Verify that all expected server names are present in output (case-insensitive).

        Args:
            output_file: Path to generated output file
            output_provider: The output provider name (to determine format)
            expected_server_names: Set of expected server names (lowercase)

        Returns:
            True if all expected server names are found, False otherwise
        """
        content = output_file.read_text(encoding="utf-8")
        output_format = PROVIDER_OUTPUT_FORMAT.get(output_provider)

        found_servers: set[str] = set()

        if output_format == ConfigFormat.JSON:
            data = json.loads(content)
            for key in ["mcpServers", "servers", "mcp"]:
                if key in data and isinstance(data[key], dict):
                    found_servers.update(server.lower() for server in data[key])

        elif output_format == ConfigFormat.TOML:
            data = toml.loads(content)
            if "mcp_servers" in data:
                servers = data["mcp_servers"]
                if isinstance(servers, dict):
                    found_servers.update(server.lower() for server in servers)
                elif isinstance(servers, list):
                    for server in servers:
                        if "name" in server:
                            found_servers.add(server["name"].lower())

        return expected_server_names.issubset(found_servers)
