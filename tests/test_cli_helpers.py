"""Tests for CLI helper utilities."""

import pytest
import time
from mcp_config_converter.cli_helpers import (
    retry_with_backoff,
    validate_format_choice,
    validate_provider_choice,
    get_provider_config,
)


class TestValidation:
    """Tests for validation functions."""

    def test_validate_format_choice_valid(self):
        """Test format validation with valid choices."""
        assert validate_format_choice("json") is True
        assert validate_format_choice("yaml") is True
        assert validate_format_choice("toml") is True

    def test_validate_format_choice_invalid(self):
        """Test format validation with invalid choices."""
        assert validate_format_choice("xml") is False
        assert validate_format_choice("invalid") is False
        assert validate_format_choice("") is False

    def test_validate_provider_choice_valid(self):
        """Test provider validation with valid choices."""
        assert validate_provider_choice("claude") is True
        assert validate_provider_choice("gemini") is True
        assert validate_provider_choice("vscode") is True
        assert validate_provider_choice("opencode") is True

    def test_validate_provider_choice_invalid(self):
        """Test provider validation with invalid choices."""
        assert validate_provider_choice("openai") is False
        assert validate_provider_choice("invalid") is False
        assert validate_provider_choice("") is False


class TestProviderConfig:
    """Tests for provider configuration."""

    def test_get_provider_config_claude(self):
        """Test getting Claude provider config."""
        config = get_provider_config("claude")
        assert config["name"] == "Claude"
        assert "api_base" in config

    def test_get_provider_config_gemini(self):
        """Test getting Gemini provider config."""
        config = get_provider_config("gemini")
        assert config["name"] == "Gemini"
        assert "api_base" in config

    def test_get_provider_config_vscode(self):
        """Test getting VS Code provider config."""
        config = get_provider_config("vscode")
        assert config["name"] == "VS Code"
        assert config["type"] == "editor_plugin"

    def test_get_provider_config_invalid(self):
        """Test getting config for invalid provider."""
        config = get_provider_config("invalid")
        assert config == {}


class TestRetry:
    """Tests for retry decorator."""

    def test_retry_success_on_first_attempt(self):
        """Test retry decorator when function succeeds immediately."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_func()
        assert result == "success"
        assert call_count == 1

    def test_retry_success_after_failures(self):
        """Test retry decorator when function succeeds after failures."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        def eventually_success_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not yet")
            return "success"

        result = eventually_success_func()
        assert result == "success"
        assert call_count == 3

    def test_retry_all_attempts_fail(self):
        """Test retry decorator when all attempts fail."""
        call_count = 0

        @retry_with_backoff(max_retries=2, initial_delay=0.1)
        def always_fail_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_fail_func()
        
        assert call_count == 3  # Initial attempt + 2 retries

    def test_retry_respects_exception_filter(self):
        """Test retry decorator only catches specified exceptions."""
        
        @retry_with_backoff(max_retries=2, initial_delay=0.1, exceptions=(ValueError,))
        def specific_exception_func():
            raise TypeError("Wrong exception type")

        with pytest.raises(TypeError, match="Wrong exception type"):
            specific_exception_func()
