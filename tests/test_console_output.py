# ruff: noqa: S101  # asserts are intended in tests
from unittest.mock import patch

from typer.testing import CliRunner

from mcp_config_converter.cli import app


def test_console_output_includes_llm_details() -> None:
    runner = CliRunner()

    with patch("mcp_config_converter.cli.convert.LiteLLMClient") as MockClient, patch("mcp_config_converter.cli.convert.ConfigTransformer") as MockTransformer:
        # Setup mocks
        mock_client_instance = MockClient.return_value
        mock_client_instance.provider = "test-provider"
        mock_client_instance.model = "test-model"

        mock_transformer_instance = MockTransformer.return_value
        mock_transformer_instance.transform.return_value = '{"mock": "result"}'

        result = runner.invoke(
            app,
            [
                "convert",
                "--input-content",
                "{}",
                "--provider",
                "claude",
                "--llm-provider",
                "test-provider",
                "--llm-model",
                "test-model",
                "--llm-api-key",
                "dummy",
            ],
        )

        assert result.exit_code == 0
        output = result.output

        print("\n--- CLI OUTPUT ---")
        print(output)
        print("------------------\n")

        # Check for presence of LLM details
        # These are expected to FAIL before the fix
        assert "LLM Provider: test-provider" in output
        assert "LLM Model: test-model" in output
