"""Tests for LiteLLM provider."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from mcp_config_converter.llm.litellm_provider import LiteLLMProvider, MODEL_MAPPINGS


class TestLiteLLMProvider:
    """Tests for LiteLLMProvider class."""

    def test_initialization_with_default_model(self) -> None:
        """Test provider initialization with default model."""
        provider = LiteLLMProvider()
        assert provider.PROVIDER_NAME == "litellm"
        assert provider.model == "gpt-4o-mini"
        assert provider._litellm_model == "gpt-4o-mini"

    def test_initialization_with_custom_model(self) -> None:
        """Test provider initialization with custom model."""
        provider = LiteLLMProvider(model="gpt-4")
        assert provider.model == "gpt-4"
        assert provider._litellm_model == "gpt-4"

    def test_model_mapping(self) -> None:
        """Test that friendly model names are mapped correctly."""
        # Test OpenAI mapping
        provider = LiteLLMProvider(model="gpt-oss-20b")
        assert provider._litellm_model == "gpt-4o-mini"

        # Test Claude mapping
        provider = LiteLLMProvider(model="claude-3-5-sonnet-20241022")
        assert provider._litellm_model == "claude-3-5-sonnet-20241022"

        # Test Gemini mapping
        provider = LiteLLMProvider(model="gemini-2.5-flash")
        assert provider._litellm_model == "gemini/gemini-2.0-flash-exp"

        # Test Ollama mapping
        provider = LiteLLMProvider(model="ollama/llama2")
        assert provider._litellm_model == "ollama/llama2"

        # Test unmapped model (should pass through)
        provider = LiteLLMProvider(model="custom-model")
        assert provider._litellm_model == "custom-model"

    def test_is_local_model(self) -> None:
        """Test local model detection."""
        provider = LiteLLMProvider()

        assert provider._is_local_model("ollama/llama2") is True
        assert provider._is_local_model("ollama_mistral") is True
        assert provider._is_local_model("gpt-4") is False
        assert provider._is_local_model("claude-3") is False

    def test_available_models(self) -> None:
        """Test that available models returns model mappings."""
        provider = LiteLLMProvider()
        models = provider.available_models

        assert models is not None
        assert len(models) > 0
        assert "gpt-4" in models
        assert "claude-3-5-sonnet-20241022" in models
        assert "gemini-2.5-flash" in models
        assert "ollama/llama2" in models

    def test_api_key_detection_openai(self) -> None:
        """Test API key detection for OpenAI models."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            provider = LiteLLMProvider(model="gpt-4")
            api_key = provider._get_api_key_for_model("gpt-4")
            assert api_key == "test-key"

    def test_api_key_detection_claude(self) -> None:
        """Test API key detection for Claude models."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-claude-key"}, clear=False):
            provider = LiteLLMProvider(model="claude-3-5-sonnet-20241022")
            api_key = provider._get_api_key_for_model("claude-3-5-sonnet-20241022")
            assert api_key == "test-claude-key"

    def test_api_key_detection_gemini(self) -> None:
        """Test API key detection for Gemini models."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-google-key"}, clear=False):
            provider = LiteLLMProvider(model="gemini-2.5-flash")
            api_key = provider._get_api_key_for_model("gemini/gemini-2.0-flash-exp")
            assert api_key == "test-google-key"

    def test_api_key_detection_ollama(self) -> None:
        """Test that Ollama models don't require API key."""
        provider = LiteLLMProvider(model="ollama/llama2")
        api_key = provider._get_api_key_for_model("ollama/llama2")
        assert api_key is None

    def test_explicit_api_key(self) -> None:
        """Test that explicit API key takes precedence."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}, clear=False):
            provider = LiteLLMProvider(api_key="explicit-key", model="gpt-4")
            api_key = provider._get_api_key_for_model("gpt-4")
            assert api_key == "explicit-key"

    def test_validate_config_with_api_key(self) -> None:
        """Test config validation with API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            provider = LiteLLMProvider(model="gpt-4")
            assert provider.validate_config() is True

    def test_validate_config_without_api_key(self) -> None:
        """Test config validation without API key for cloud models."""
        # Clear all API key environment variables
        env_clear = {
            key: ""
            for key in os.environ
            if "API_KEY" in key or "GOOGLE_API_KEY" in key or "GEMINI_API_KEY" in key
        }
        with patch.dict(os.environ, env_clear, clear=False):
            provider = LiteLLMProvider(model="gpt-4")
            assert provider.validate_config() is False

    def test_validate_config_ollama_no_key_required(self) -> None:
        """Test config validation for Ollama (no API key required)."""
        provider = LiteLLMProvider(model="ollama/llama2")
        assert provider.validate_config() is True

    @patch("mcp_config_converter.llm.litellm_provider.completion")
    def test_generate_basic(self, mock_completion: Mock) -> None:
        """Test basic text generation."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        provider = LiteLLMProvider(api_key="test-key", model="gpt-4")
        result = provider.generate("Test prompt")

        assert result == "Generated text"
        mock_completion.assert_called_once()
        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["model"] == "gpt-4"
        assert len(call_kwargs["messages"]) == 1
        assert call_kwargs["messages"][0]["role"] == "user"
        assert call_kwargs["messages"][0]["content"] == "Test prompt"

    @patch("mcp_config_converter.llm.litellm_provider.completion")
    def test_generate_with_system_prompt(self, mock_completion: Mock) -> None:
        """Test text generation with system prompt."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        provider = LiteLLMProvider(api_key="test-key", model="gpt-4")
        result = provider.generate("Test prompt", system_prompt="You are a helpful assistant")

        assert result == "Generated text"
        call_kwargs = mock_completion.call_args[1]
        assert len(call_kwargs["messages"]) == 2
        assert call_kwargs["messages"][0]["role"] == "system"
        assert call_kwargs["messages"][0]["content"] == "You are a helpful assistant"
        assert call_kwargs["messages"][1]["role"] == "user"

    @patch("mcp_config_converter.llm.litellm_provider.completion")
    def test_generate_with_max_tokens(self, mock_completion: Mock) -> None:
        """Test text generation with custom max_tokens."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        provider = LiteLLMProvider(api_key="test-key", model="gpt-4")
        result = provider.generate("Test prompt", max_tokens=2048)

        assert result == "Generated text"
        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["max_tokens"] == 2048

    @patch("mcp_config_converter.llm.litellm_provider.completion")
    @patch("mcp_config_converter.llm.litellm_provider.time.sleep")
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

        provider = LiteLLMProvider(api_key="test-key", model="gpt-4", max_retries=3, retry_delay=1.0)
        result = provider.generate("Test prompt")

        assert result == "Generated text"
        assert mock_completion.call_count == 3
        assert mock_sleep.call_count == 2
        # Check exponential backoff: 1.0 * 2^0 = 1.0, 1.0 * 2^1 = 2.0
        assert mock_sleep.call_args_list[0][0][0] == 1.0
        assert mock_sleep.call_args_list[1][0][0] == 2.0

    @patch("mcp_config_converter.llm.litellm_provider.completion")
    @patch("mcp_config_converter.llm.litellm_provider.time.sleep")
    def test_retry_exhaustion(self, mock_sleep: Mock, mock_completion: Mock) -> None:
        """Test that retry logic gives up after max_retries."""
        from litellm.exceptions import RateLimitError

        mock_completion.side_effect = RateLimitError("Rate limit", "test", "test")

        provider = LiteLLMProvider(api_key="test-key", model="gpt-4", max_retries=2, retry_delay=1.0)

        with pytest.raises(RuntimeError, match="LiteLLM generation failed after 2 retries"):
            provider.generate("Test prompt")

        assert mock_completion.call_count == 2
        assert mock_sleep.call_count == 1  # Only sleep between retries, not after last

    @patch("mcp_config_converter.llm.litellm_provider.completion")
    def test_base_url_parameter(self, mock_completion: Mock) -> None:
        """Test that base_url is passed correctly."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        provider = LiteLLMProvider(
            api_key="test-key",
            model="gpt-4",
            base_url="https://custom.api.com/v1"
        )
        result = provider.generate("Test prompt")

        assert result == "Generated text"
        call_kwargs = mock_completion.call_args[1]
        assert call_kwargs["api_base"] == "https://custom.api.com/v1"

    @patch("mcp_config_converter.llm.litellm_provider.completion")
    def test_model_mapping_in_generate(self, mock_completion: Mock) -> None:
        """Test that model mapping is applied in generate call."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_completion.return_value = mock_response

        # Use a friendly name that maps to a different LiteLLM model
        provider = LiteLLMProvider(api_key="test-key", model="gemini-2.5-flash")
        result = provider.generate("Test prompt")

        assert result == "Generated text"
        call_kwargs = mock_completion.call_args[1]
        # Check that the LiteLLM model identifier is used, not the friendly name
        assert call_kwargs["model"] == "gemini/gemini-2.0-flash-exp"
