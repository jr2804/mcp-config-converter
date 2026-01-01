"""Tests for LiteLLM client."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from mcp_config_converter.llm.client import (
    LiteLLMClient,
    PROVIDER_DEFAULT_MODELS,
    detect_available_providers,
    create_client_from_env,
)


class TestLiteLLMClient:
    """Tests for LiteLLMClient class."""

    def test_initialization_with_provider_and_model(self) -> None:
        """Test client initialization with provider and model."""
        client = LiteLLMClient(provider="openai", model="gpt-4")
        assert client.provider == "openai"
        assert client.model == "gpt-4"

    def test_initialization_with_provider_only(self) -> None:
        """Test client initialization with provider only (uses default model)."""
        client = LiteLLMClient(provider="openai")
        assert client.provider == "openai"
        assert client.model == PROVIDER_DEFAULT_MODELS["openai"]

    def test_initialization_with_model_only(self) -> None:
        """Test client initialization with model only."""
        client = LiteLLMClient(model="gpt-4")
        assert client.model == "gpt-4"

    def test_initialization_defaults(self) -> None:
        """Test client initialization with no parameters uses fallback."""
        client = LiteLLMClient()
        assert client.model == "gpt-4o-mini"  # Fallback default

    def test_api_key_from_parameter(self) -> None:
        """Test that explicit API key is used."""
        client = LiteLLMClient(provider="openai", api_key="explicit-key")
        assert client.api_key == "explicit-key"

    def test_api_key_from_env_openai(self) -> None:
        """Test API key detection from environment for OpenAI."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            client = LiteLLMClient(provider="openai")
            assert client.api_key == "test-key"

    def test_api_key_from_env_anthropic(self) -> None:
        """Test API key detection from environment for Anthropic."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-claude-key"}, clear=False):
            client = LiteLLMClient(provider="anthropic")
            assert client.api_key == "test-claude-key"

    def test_api_key_from_env_gemini(self) -> None:
        """Test API key detection from environment for Gemini."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-google-key"}, clear=False):
            client = LiteLLMClient(provider="gemini")
            assert client.api_key == "test-google-key"

    def test_api_key_from_env_multiple_vars(self) -> None:
        """Test API key detection when multiple env vars are possible."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "gemini-key"}, clear=False):
            client = LiteLLMClient(provider="gemini")
            assert client.api_key == "gemini-key"

    def test_api_key_explicit_overrides_env(self) -> None:
        """Test that explicit API key takes precedence over environment."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}, clear=False):
            client = LiteLLMClient(provider="openai", api_key="explicit-key")
            assert client.api_key == "explicit-key"

    def test_validate_config_with_api_key(self) -> None:
        """Test config validation with API key."""
        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4")
        assert client.validate_config() is True

    def test_validate_config_without_api_key(self) -> None:
        """Test config validation without API key for cloud models."""
        client = LiteLLMClient(provider="openai", model="gpt-4")
        # Should fail if no API key in environment
        with patch.dict(os.environ, {}, clear=True):
            client_no_key = LiteLLMClient(provider="openai", model="gpt-4")
            assert client_no_key.validate_config() is False

    def test_validate_config_ollama_no_key_required(self) -> None:
        """Test config validation for Ollama (no API key required)."""
        client = LiteLLMClient(provider="ollama", model="llama2")
        assert client.validate_config() is True

    def test_validate_config_no_model(self) -> None:
        """Test config validation fails without model."""
        client = LiteLLMClient(provider="openai", api_key="test-key")
        client.model = None  # Force no model
        assert client.validate_config() is False

    @patch("mcp_config_converter.llm.client.completion")
    def test_generate_basic(self, mock_completion: Mock) -> None:
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

    @patch("mcp_config_converter.llm.client.completion")
    def test_generate_with_system_prompt(self, mock_completion: Mock) -> None:
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

    @patch("mcp_config_converter.llm.client.completion")
    def test_generate_with_max_tokens(self, mock_completion: Mock) -> None:
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

    @patch("mcp_config_converter.llm.client.completion")
    @patch("mcp_config_converter.llm.client.time.sleep")
    def test_retry_on_rate_limit(self, mock_sleep: Mock, mock_completion: Mock) -> None:
        """Test retry logic on rate limit errors."""
        from litellm.exceptions import RateLimitError

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

    @patch("mcp_config_converter.llm.client.completion")
    @patch("mcp_config_converter.llm.client.time.sleep")
    def test_retry_exhaustion(self, mock_sleep: Mock, mock_completion: Mock) -> None:
        """Test that retry logic gives up after max_retries."""
        from litellm.exceptions import RateLimitError

        mock_completion.side_effect = RateLimitError("Rate limit", "test", "test")

        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4", max_retries=2, retry_delay=1.0)

        with pytest.raises(RuntimeError, match="LiteLLM generation failed after 2 retries"):
            client.generate("Test prompt")

        assert mock_completion.call_count == 2
        assert mock_sleep.call_count == 1  # Only sleep between retries, not after last

    @patch("mcp_config_converter.llm.client.completion")
    def test_base_url_parameter(self, mock_completion: Mock) -> None:
        """Test that base_url is passed correctly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        client = LiteLLMClient(
            provider="openai",
            api_key="test-key",
            model="gpt-4",
            base_url="https://custom.api.com/v1"
        )
        result = client.generate("Test prompt")

        assert result == "Generated text"
        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["api_base"] == "https://custom.api.com/v1"


class TestDetectAvailableProviders:
    """Tests for detect_available_providers function."""

    def test_detect_no_providers(self) -> None:
        """Test detection when no API keys are set."""
        with patch.dict(os.environ, {}, clear=True):
            providers = detect_available_providers()
            # Ollama should still be available (no key required)
            ollama_providers = [p for p in providers if p[0] == "ollama"]
            assert len(ollama_providers) == 1

    def test_detect_openai_provider(self) -> None:
        """Test detection of OpenAI provider."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            assert "openai" in provider_names

    def test_detect_multiple_providers(self) -> None:
        """Test detection of multiple providers."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "openai-key",
            "ANTHROPIC_API_KEY": "anthropic-key",
            "GOOGLE_API_KEY": "google-key",
        }, clear=False):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            assert "openai" in provider_names
            assert "anthropic" in provider_names
            assert "gemini" in provider_names

    def test_detect_provider_with_multiple_env_vars(self) -> None:
        """Test detection when provider has multiple possible env vars."""
        # Test with GEMINI_API_KEY
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=False):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            assert "gemini" in provider_names

        # Test with GOOGLE_API_KEY
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}, clear=False):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            assert "gemini" in provider_names


class TestCreateClientFromEnv:
    """Tests for create_client_from_env function."""

    def test_create_from_explicit_config(self) -> None:
        """Test client creation from explicit MCP_CONFIG_CONF_* variables."""
        with patch.dict(os.environ, {
            "MCP_CONFIG_CONF_LLM_PROVIDER_TYPE": "openai",
            "MCP_CONFIG_CONF_LLM_MODEL": "gpt-4",
            "MCP_CONFIG_CONF_API_KEY": "test-key",
        }, clear=False):
            client = create_client_from_env()
            assert client is not None
            assert client.provider == "openai"
            assert client.model == "gpt-4"
            assert client.api_key == "test-key"

    def test_create_from_auto_detect(self) -> None:
        """Test client creation from auto-detected providers."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            client = create_client_from_env()
            assert client is not None
            assert client.provider == "openai"
            assert client.api_key == "test-key"

    def test_create_returns_none_when_no_config(self) -> None:
        """Test that None is returned when no configuration is found."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock detect_available_providers to return empty list
            with patch("mcp_config_converter.llm.client.detect_available_providers", return_value=[]):
                client = create_client_from_env()
                assert client is None

    def test_create_with_base_url(self) -> None:
        """Test client creation with custom base URL."""
        with patch.dict(os.environ, {
            "MCP_CONFIG_CONF_LLM_PROVIDER_TYPE": "openai",
            "MCP_CONFIG_CONF_LLM_BASE_URL": "https://custom.api.com/v1",
            "MCP_CONFIG_CONF_API_KEY": "test-key",
        }, clear=False):
            client = create_client_from_env()
            assert client is not None
            assert client.base_url == "https://custom.api.com/v1"
