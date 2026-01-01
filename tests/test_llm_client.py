"""Tests for LiteLLM client."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from mcp_config_converter.llm.client import (
    LiteLLMClient,
    create_client_from_env,
    detect_available_providers,
    PROVIDER_DEFAULT_MODELS,
)


class TestLiteLLMClient:
    """Tests for LiteLLMClient class."""

    def test_initialization_with_defaults(self) -> None:
        """Test client initialization with defaults."""
        client = LiteLLMClient()
        assert client.provider is None
        assert client.model == "gpt-4o-mini"  # Fallback default
        assert client.api_key is None

    def test_initialization_with_provider(self) -> None:
        """Test client initialization with provider."""
        client = LiteLLMClient(provider="openai", api_key="test-key")
        assert client.provider == "openai"
        assert client.model == PROVIDER_DEFAULT_MODELS["openai"]
        assert client.api_key == "test-key"

    def test_initialization_with_custom_model(self) -> None:
        """Test client initialization with custom model."""
        client = LiteLLMClient(provider="openai", model="gpt-4", api_key="test-key")
        assert client.model == "gpt-4"

    def test_api_key_from_env_openai(self) -> None:
        """Test API key detection from environment for OpenAI."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}, clear=False):
            client = LiteLLMClient(provider="openai")
            assert client.api_key == "env-key"

    def test_api_key_from_env_anthropic(self) -> None:
        """Test API key detection from environment for Anthropic."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "anthropic-key"}, clear=False):
            client = LiteLLMClient(provider="anthropic")
            assert client.api_key == "anthropic-key"

    def test_api_key_from_env_gemini(self) -> None:
        """Test API key detection from environment for Gemini (multiple env vars)."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "google-key"}, clear=False):
            client = LiteLLMClient(provider="gemini")
            assert client.api_key == "google-key"

    def test_explicit_api_key_takes_precedence(self) -> None:
        """Test that explicit API key takes precedence over environment."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}, clear=False):
            client = LiteLLMClient(provider="openai", api_key="explicit-key")
            assert client.api_key == "explicit-key"

    @patch("mcp_config_converter.llm.client.completion")
    def test_generate_basic(self, mock_completion: Mock) -> None:
        """Test basic text generation."""
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

    @patch("mcp_config_converter.llm.client.completion")
    def test_generate_with_system_prompt(self, mock_completion: Mock) -> None:
        """Test text generation with system prompt."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4")
        result = client.generate("Test prompt", system_prompt="You are helpful")

        assert result == "Generated text"
        call_kwargs = mock_completion.call_args[1]
        assert len(call_kwargs["messages"]) == 2
        assert call_kwargs["messages"][0]["role"] == "system"
        assert call_kwargs["messages"][1]["role"] == "user"

    @patch("mcp_config_converter.llm.client.completion")
    @patch("mcp_config_converter.llm.client.time.sleep")
    def test_retry_on_rate_limit(self, mock_sleep: Mock, mock_completion: Mock) -> None:
        """Test retry logic on rate limit errors."""
        from litellm.exceptions import RateLimitError

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"

        # First call raises error, second succeeds
        mock_completion.side_effect = [
            RateLimitError("Rate limit", "test", "test"),
            mock_response,
        ]

        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4", max_retries=3)
        result = client.generate("Test prompt")

        assert result == "Generated text"
        assert mock_completion.call_count == 2
        assert mock_sleep.call_count == 1

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

    def test_validate_config_with_api_key(self) -> None:
        """Test config validation with API key."""
        client = LiteLLMClient(provider="openai", api_key="test-key", model="gpt-4")
        assert client.validate_config() is True

    def test_validate_config_without_api_key(self) -> None:
        """Test config validation without API key for providers that need it."""
        client = LiteLLMClient(provider="openai", model="gpt-4")
        assert client.validate_config() is False

    def test_validate_config_ollama_no_key_required(self) -> None:
        """Test config validation for Ollama (no API key required)."""
        client = LiteLLMClient(provider="ollama", model="llama2")
        assert client.validate_config() is True

    @patch("mcp_config_converter.llm.client.model_list")
    def test_get_available_models(self, mock_model_list: Mock) -> None:
        """Test getting available models."""
        mock_model_list.return_value = ["gpt-4", "gpt-3.5-turbo", "claude-3"]
        
        client = LiteLLMClient()
        models = client.get_available_models()
        
        assert "gpt-4" in models
        assert "gpt-3.5-turbo" in models


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_detect_available_providers_with_keys(self) -> None:
        """Test detecting providers with configured API keys."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "openai-key",
            "ANTHROPIC_API_KEY": "anthropic-key",
        }, clear=False):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            
            assert "openai" in provider_names
            assert "anthropic" in provider_names
            assert "ollama" in provider_names  # Ollama doesn't need API key

    def test_detect_available_providers_empty(self) -> None:
        """Test detecting providers with no API keys."""
        # Clear all API key env vars
        env_clear = {key: "" for key in os.environ if "API_KEY" in key}
        with patch.dict(os.environ, env_clear, clear=False):
            providers = detect_available_providers()
            provider_names = [p[0] for p in providers]
            
            # Should still have Ollama (no API key needed)
            assert "ollama" in provider_names

    def test_create_client_from_env_with_explicit_config(self) -> None:
        """Test creating client from explicit env vars."""
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

    def test_create_client_from_env_with_auto_detect(self) -> None:
        """Test creating client with auto-detection."""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "openai-key",
        }, clear=False):
            client = create_client_from_env()
            
            assert client is not None
            assert client.provider == "openai"
            assert client.api_key == "openai-key"

    def test_create_client_from_env_no_config(self) -> None:
        """Test creating client with no configuration."""
        # Clear all relevant env vars
        env_clear = {
            key: "" 
            for key in os.environ 
            if "API_KEY" in key or "MCP_CONFIG_CONF" in key
        }
        with patch.dict(os.environ, env_clear, clear=False):
            client = create_client_from_env()
            
            # Should return None or create Ollama client
            if client is None:
                assert True
            else:
                # Ollama doesn't require API key
                assert client.provider == "ollama"
