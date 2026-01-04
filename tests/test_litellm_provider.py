"""Tests for LiteLLM client."""
# ruff: noqa: S101  # asserts are intended in tests

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from litellm.exceptions import RateLimitError

from mcp_config_converter.llm import (
    PROVIDER_DEFAULT_MODELS,
    LiteLLMClient,
    create_client_from_env,
    detect_available_providers,
)


class TestLiteLLMClient:
    """Tests for LiteLLMClient class."""

    @staticmethod
    def test_initialization_with_provider_and_model() -> None:
        """Test client initialization with provider and model."""
        client = LiteLLMClient(provider="openai", model="gpt-4")
        assert client.provider == "openai"
        assert client.model == "gpt-4"

    @staticmethod
    def test_initialization_with_provider_only() -> None:
        """Test client initialization with provider only (uses default model)."""
        client = LiteLLMClient(provider="openai")
        assert client.provider == "openai"
        assert client.model == PROVIDER_DEFAULT_MODELS["openai"]

    @staticmethod
    def test_initialization_with_model_only() -> None:
        """Test client initialization with model only."""
        client = LiteLLMClient(model="gpt-4")
        assert client.model == "gpt-4"

    @staticmethod
    def test_initialization_defaults() -> None:
        """Test client initialization with no parameters uses fallback."""
        client = LiteLLMClient()
        assert client.model == "gpt-4o-mini"  # Fallback default

    @staticmethod
    def test_api_key_from_parameter() -> None:
        """Test that explicit API key is used."""
        client = LiteLLMClient(provider="openai", api_key="explicit-key")
        assert client.api_key == "explicit-key"

    @staticmethod
    def test_api_key_from_env_openai() -> None:
        """Test API key detection from environment for OpenAI."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            client = LiteLLMClient(provider="openai")
            assert client.api_key == "test-key"

    @staticmethod
    def test_api_key_from_env_anthropic() -> None:
        """Test API key detection from environment for Anthropic."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-claude-key"}, clear=False):
            client = LiteLLMClient(provider="anthropic")
            assert client.api_key == "test-claude-key"

    @staticmethod
    def test_api_key_from_env_gemini() -> None:
        """Test API key detection from environment for Gemini."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-google-key"}, clear=False):
            with patch.dict(
                os.environ,
                {
                    "GOOGLE_API_KEY": "test-google-key",
                    "GEMINI_API_KEY": "",
                    "GOOGLE_GENERATIVE_AI_API_KEY": "",
                },
                clear=False,
            ):
                client = LiteLLMClient(provider="gemini")
            assert client.api_key == "test-google-key"

    @staticmethod
    def test_api_key_from_env_zai() -> None:
        """Test API key detection from environment for z.ai."""
        with patch.dict(os.environ, {"ZAI_API_KEY": "test-zai-key"}, clear=False):
            client = LiteLLMClient(provider="zai")
            assert client.api_key == "test-zai-key"

    @staticmethod
    def test_api_key_from_env_multiple_vars() -> None:
        """Test API key detection when multiple env vars are possible."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "gemini-key"}, clear=False):
            client = LiteLLMClient(provider="gemini")
            assert client.api_key == "gemini-key"

    @staticmethod
    def test_api_key_explicit_overrides_env() -> None:
        """Test that explicit API key takes precedence over environment."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}, clear=False):
            client = LiteLLMClient(provider="openai", api_key="explicit-key")
            assert client.api_key == "explicit-key"

    @staticmethod
    def test_validate_config_with_api_key() -> None:
        """Test config validation with API key."""
        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4")
        assert client.validate_config() is True

    @staticmethod
    def test_validate_config_without_api_key() -> None:
        """Test config validation without API key for cloud models."""
        LiteLLMClient(provider="openai", model="gpt-4")
        # Should fail if no API key in environment
        with patch.dict(os.environ, {}, clear=True):
            client_no_key = LiteLLMClient(provider="openai", model="gpt-4")
            assert client_no_key.validate_config() is False

    @staticmethod
    def test_validate_config_ollama_no_key_required() -> None:
        """Test config validation for Ollama (no API key required)."""
        client = LiteLLMClient(provider="ollama", model="llama2")
        assert client.validate_config() is True

    @staticmethod
    def test_validate_config_no_model() -> None:
        """Test config validation fails without model."""
        client = LiteLLMClient(provider="openai", api_key="test-key")
        client.model = None  # Force no model
        assert client.validate_config() is False

    @staticmethod
    @patch("mcp_config_converter.llm.client.completion")
    def test_generate_basic(mock_completion: Mock) -> None:
        """Test basic text generation."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4")
        result = client.generate("Test prompt")

        assert result == "Generated text"
        mock_completion.assert_called_once()
        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["model"] == "gpt-4"
        assert len(call_kwargs["messages"]) == 1
        assert call_kwargs["messages"][0]["role"] == "user"
        assert call_kwargs["messages"][0]["content"] == "Test prompt"

    @staticmethod
    @patch("mcp_config_converter.llm.client.completion")
    def test_generate_with_system_prompt(mock_completion: Mock) -> None:
        """Test text generation with system prompt."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4")
        result = client.generate("Test prompt", system_prompt="You are a helpful assistant")

        assert result == "Generated text"
        call_kwargs = mock_completion.call_args[1]
        assert len(call_kwargs["messages"]) == 2
        assert call_kwargs["messages"][0]["role"] == "system"
        assert call_kwargs["messages"][0]["content"] == "You are a helpful assistant"
        assert call_kwargs["messages"][1]["role"] == "user"

    @staticmethod
    @patch("mcp_config_converter.llm.client.completion")
    def test_generate_with_max_tokens(mock_completion: Mock) -> None:
        """Test text generation with custom max_tokens."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4")
        result = client.generate("Test prompt", max_tokens=2048)

        assert result == "Generated text"
        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["max_tokens"] == 2048

    @staticmethod
    @patch("mcp_config_converter.llm.client.completion")
    @patch("mcp_config_converter.llm.client.time.sleep")
    def test_retry_on_rate_limit(mock_sleep: Mock, mock_completion: Mock) -> None:
        """Test retry logic on rate limit errors."""
        # First two calls raise RateLimitError, third succeeds
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"

        mock_completion.side_effect = [
            RateLimitError("Rate limit", "test", "test"),
            RateLimitError("Rate limit", "test", "test"),
            mock_response,
        ]

        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4", max_retries=3, retry_delay=1.0)
        result = client.generate("Test prompt")

        assert result == "Generated text"
        assert mock_completion.call_count == 3
        assert mock_sleep.call_count == 2
        # Check exponential backoff: 1.0 * 2^0 = 1.0, 1.0 * 2^1 = 2.0
        assert mock_sleep.call_args_list[0][0][0] == 1.0
        assert mock_sleep.call_args_list[1][0][0] == 2.0

    @staticmethod
    @patch("mcp_config_converter.llm.client.completion")
    @patch("mcp_config_converter.llm.client.time.sleep")
    def test_retry_exhaustion(mock_sleep: Mock, mock_completion: Mock) -> None:
        """Test that retry logic gives up after max_retries."""
        mock_completion.side_effect = RateLimitError("Rate limit", "test", "test")

        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4", max_retries=2, retry_delay=1.0)

        with pytest.raises(RuntimeError, match="LiteLLM generation failed after 2 retries"):
            client.generate("Test prompt")

        assert mock_completion.call_count == 2
        assert mock_sleep.call_count == 1  # Only sleep between retries, not after last

    @staticmethod
    @patch("mcp_config_converter.llm.client.completion")
    def test_base_url_parameter(mock_completion: Mock) -> None:
        """Test that base_url is passed correctly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4", base_url="https://custom.api.com/v1")
        result = client.generate("Test prompt")

        assert result == "Generated text"
        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["api_base"] == "https://custom.api.com/v1"


class TestDetectAvailableProviders:
    """Tests for detect_available_providers function."""

    @staticmethod
    def test_detect_no_providers() -> None:
        """Test detection when no API keys are set."""
        with patch.dict(os.environ, {}, clear=True):
            providers = detect_available_providers()
            # Ollama should still be available (no key required)
            ollama_providers = [p for p in providers if p[0] == "ollama"]
            assert len(ollama_providers) == 1

    @staticmethod
    def test_detect_openai_provider() -> None:
        """Test detection of OpenAI provider."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            assert "openai" in provider_names

    @staticmethod
    def test_detect_multiple_providers() -> None:
        """Test detection of multiple providers."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "openai-key",
                "ANTHROPIC_API_KEY": "anthropic-key",
                "GOOGLE_API_KEY": "google-key",
            },
            clear=False,
        ):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            assert "openai" in provider_names
            assert "anthropic" in provider_names
            assert "gemini" in provider_names

    @staticmethod
    def test_detect_provider_with_multiple_env_vars() -> None:
        """Test detection when provider has multiple possible env vars."""
        # Test with GEMINI_API_KEY
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "GOOGLE_API_KEY": "", "GOOGLE_GENERATIVE_AI_API_KEY": ""}, clear=False):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            assert "gemini" in provider_names

        # Test with GOOGLE_API_KEY
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key", "GEMINI_API_KEY": "", "GOOGLE_GENERATIVE_AI_API_KEY": ""}, clear=False):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            assert "gemini" in provider_names

    @staticmethod
    def test_detect_zai_provider() -> None:
        """Test detection of z.ai provider via env var."""
        with patch.dict(os.environ, {"ZAI_API_KEY": "test-key"}, clear=False):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            assert "zai" in provider_names


class TestCreateClientFromEnv:
    """Tests for create_client_from_env function."""

    @staticmethod
    def test_create_from_explicit_config() -> None:
        """Test client creation from explicit MCP_CONFIG_CONF_* variables."""
        with patch.dict(
            os.environ,
            {
                "MCP_CONFIG_CONF_LLM_PROVIDER_TYPE": "openai",
                "MCP_CONFIG_CONF_LLM_MODEL": "gpt-4",
                "MCP_CONFIG_CONF_API_KEY": "test-key",
            },
            clear=False,
        ):
            client = create_client_from_env()
            assert client is not None
            assert client.provider == "openai"
            assert client.model == "gpt-4"
            assert client.api_key == "test-key"

    @staticmethod
    def test_create_from_auto_detect() -> None:
        """Test client creation from auto-detected providers."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            client = create_client_from_env()
            assert client is not None
            assert client.provider == "openai"
            assert client.api_key == "test-key"

    @staticmethod
    def test_create_returns_none_when_no_config() -> None:
        """Test that None is returned when no configuration is found."""
        with patch.dict(os.environ, {}, clear=True), patch("mcp_config_converter.llm.client.detect_available_providers", return_value=[]):
            client = create_client_from_env()
            assert client is None

    @staticmethod
    def test_create_with_base_url() -> None:
        """Test client creation with custom base URL."""
        with patch.dict(
            os.environ,
            {
                "MCP_CONFIG_CONF_LLM_PROVIDER_TYPE": "openai",
                "MCP_CONFIG_CONF_LLM_BASE_URL": "https://custom.api.com/v1",
                "MCP_CONFIG_CONF_API_KEY": "test-key",
            },
            clear=False,
        ):
            client = create_client_from_env()
            assert client is not None
            assert client.base_url == "https://custom.api.com/v1"
