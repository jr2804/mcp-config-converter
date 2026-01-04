"""Tests for CLI functionality."""
# ruff: noqa: S101  # asserts are intended in tests

import json
import os
import re
from pathlib import Path

import pytest
import toml
from typer.testing import CliRunner

from mcp_config_converter.cli import app
from mcp_config_converter.cli.constants import SUPPORTED_PROVIDERS
from mcp_config_converter.llm import PROVIDER_API_KEY_ENV_VARS, LiteLLMClient
from mcp_config_converter.types import PROVIDER_OUTPUT_FORMAT, ConfigFormat

TEST_DATA_DIR = Path("tests/data")
TEST_INPUT_FILE = TEST_DATA_DIR / "config_vscode.json"
TEST_OUTPUT_ROOT = Path("tests/temp")


def _parse_test_llm_providers(input_str: str) -> list[tuple[str, str]]:
    """Parse LLM provider/model specifications from environment variable.

    Supports multiple formats:
    - Single: "openrouter/subprovider/model"
    - List (comma): "ollama/gemma3, deepseek/deepseek-chat"
    - List (semicolon): "ollama/gemma3; deepseek/deepseek-chat"
    - List (colon): "ollama/gemma3: deepseek/deepseek-chat"
    - Mixed separators: "ollama/gemma3; deepseek/deepseek-chat,sambanova/model"

    Args:
        input_str: Comma/semicolon/colon-separated provider/model specs

    Returns:
        List of (provider, model) tuples

    Raises:
        ValueError: If parsing fails at any point
    """
    configs = []

    for part in re.split(r"[,;:]", input_str.strip()):
        part = part.strip()
        if not part:
            raise ValueError(f"Empty provider specification in: {input_str}")

        if "/" in part:
            parts = part.split("/", 1)
            provider = parts[0].strip()
            model = parts[1].strip()
        else:
            provider = part.strip()
            model = "-1"

        if not provider:
            raise ValueError(f"Missing provider in specification: {part}")
        if not model:
            raise ValueError(f"Missing model in specification: {part}")

        configs.append((provider, model))

    return configs


def _generate_test_params() -> list:
    """Generate test parameters for all provider combinations.

    Respects MCP_CONFIG_CONF_MAX_TESTS environment variable to limit tests.
    Respects MCP_CONFIG_CONF_TEST_LLM_PROVIDERS to specify providers.

    Raises:
        ValueError: If test provider parsing fails or invalid configuration
    """
    params = []

    test_llm_providers_str = os.getenv("MCP_CONFIG_CONF_TEST_LLM_PROVIDERS")
    max_tests = int(os.getenv("MCP_CONFIG_CONF_MAX_TESTS", "2"))

    llm_configs = _parse_test_llm_providers(test_llm_providers_str) if test_llm_providers_str else [("ollama", "-1")]

    for output_provider in SUPPORTED_PROVIDERS:
        for i, (llm_provider, llm_model) in enumerate(llm_configs):
            if i >= max_tests:
                break

            params.append(
                pytest.param(
                    output_provider,
                    llm_provider,
                    llm_model,
                    id=f"{output_provider}-{llm_provider}",
                )
            )

    return params


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
        """Test convert command with provider combinations.

        Test behavior depends on environment variables:
        - If MCP_CONFIG_CONF_TEST_LLM_PROVIDERS is set: Tests specified providers
        - Otherwise: Tests ollama/-1 (default, no cost)
        - MCP_CONFIG_CONF_MAX_TESTS: Limits tests per output provider (default: 2)

        Makes actual LLM calls if API keys are configured.
        Test suite fails if API key is missing or provider is invalid.
        VS Code to VS Code conversions are skipped.
        """
        # Skip vscode-to-vscode conversions (no conversion needed)
        if output_provider == "vscode":
            pytest.skip("VS Code to VS Code conversion is not applicable")

        TestCLI._ensure_provider_available(llm_provider, llm_model)

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
                "--llm-provider",
                llm_provider,
                "--llm-model",
                llm_model,
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
        assert "gemini" in result.stdout
        # Check for new columns - note: column headers are truncated in display
        # The table shows "Environment" (truncated from "Environment Variable")
        # and "Override" (truncated from "Override Value")
        assert "Environment" in result.stdout
        assert "Override" in result.stdout

    @staticmethod
    def test_show_defaults_with_env_var_override(runner: CliRunner) -> None:
        """Test show-defaults command with environment variable override."""
        # Set environment variable for vscode provider
        env_var_name = "MCP_CONFIG_CONV_VSCODE_DEFAULT_OUTPUT"
        override_path = "/custom/path/vscode_mcp.json"
        original_value = os.getenv(env_var_name)

        try:
            # Set the environment variable
            os.environ[env_var_name] = override_path

            # Run the show-defaults command
            result = runner.invoke(app, ["show-defaults"])
            assert result.exit_code == 0
            assert "Default Output Paths" in result.stdout

            # Check that the override value appears in the output
            # The table shows truncated values, so check for partial matches
            # Environment variable name is truncated to "MCP_CONFIG_..."
            assert "MCP_CONFIG_" in result.stdout

            # The override path should appear in the output (may be truncated or normalized)
            # On Windows, paths get normalized with backslashes
            if "\\custom\\" in result.stdout or "/custom/" in result.stdout:
                # Path appears in output (either Windows or Unix format)
                pass
            else:
                # Check for truncated version
                assert "custom" in result.stdout or "vscode_mcp" in result.stdout

            # Also check that vscode provider shows something other than the default
            # The default path ".vscode/mcp.json" should not appear for vscode row
            # when override is set (though it might appear for other providers)
            # We'll check that the vscode row shows a path containing "custom"
            vscode_line = None
            for line in result.stdout.split("\n"):
                if "vscode" in line and "|" in line:
                    vscode_line = line
                    break

            if vscode_line:
                # The vscode line should contain "custom" or the override path
                assert "custom" in vscode_line or "vscode_mcp" in vscode_line

        finally:
            # Clean up - restore original environment variable
            if original_value is not None:
                os.environ[env_var_name] = original_value
            else:
                os.environ.pop(env_var_name, None)

    @staticmethod
    def _ensure_provider_available(provider: str, model: str | int) -> None:
        """Ensure LLM provider can be instantiated, fail test if not.

        Args:
            provider: LLM provider name
            model: Model name or index

        Raises:
            ValueError: If provider cannot be instantiated or API key is missing
        """
        # Check if provider requires API key
        env_vars = PROVIDER_API_KEY_ENV_VARS.get(provider, [])
        if env_vars:
            has_api_key = any(os.getenv(var) for var in env_vars)
            if not has_api_key:
                raise ValueError(f"API key required for provider '{provider}' but none configured. Expected one of: {', '.join(env_vars)}")

        # Try to instantiate client
        try:
            LiteLLMClient(provider=provider, model=model)
        except ValueError as e:
            raise ValueError(f"Failed to instantiate client for provider '{provider}': {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to instantiate client for provider '{provider}': {e}") from e

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
