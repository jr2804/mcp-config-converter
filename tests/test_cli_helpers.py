"""Tests for CLI helper utilities."""

from typing import Never

import pytest

from mcp_config_converter.cli.utils import (
    retry_with_backoff,
    validate_format_choice,
    validate_provider_choice,
)


class TestValidation:
    """Tests for validation functions."""

    @staticmethod
    def test_validate_format_choice_valid() -> None:
        """Test format validation with valid choices."""
        assert validate_format_choice("claude") is True
        assert validate_format_choice("gemini") is True
        assert validate_format_choice("vscode") is True

    @staticmethod
    def test_validate_format_choice_invalid() -> None:
        """Test format validation with invalid choices."""
        assert validate_format_choice("json") is False  # Not a provider format
        assert validate_format_choice("invalid") is False
        assert validate_format_choice("") is False

    @staticmethod
    def test_validate_provider_choice_valid() -> None:
        """Test provider validation with valid choices."""
        assert validate_provider_choice("claude") is True
        assert validate_provider_choice("gemini") is True
        assert validate_provider_choice("mistral") is True
        assert validate_provider_choice("vscode") is True
        assert validate_provider_choice("opencode") is True

    @staticmethod
    def test_validate_provider_choice_invalid() -> None:
        """Test provider validation with invalid choices."""
        assert validate_provider_choice("openai") is False
        assert validate_provider_choice("invalid") is False
        assert validate_provider_choice("") is False


class TestRetry:
    """Tests for retry decorator."""

    @staticmethod
    def test_retry_success_on_first_attempt() -> None:
        """Test retry decorator when function succeeds immediately."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        def success_func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_func()
        assert result == "success"
        assert call_count == 1

    @staticmethod
    def test_retry_success_after_failures() -> None:
        """Test retry decorator when function succeeds after failures."""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        def eventually_success_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not yet")
            return "success"

        result = eventually_success_func()
        assert result == "success"
        assert call_count == 3

    @staticmethod
    def test_retry_all_attempts_fail() -> None:
        """Test retry decorator when all attempts fail."""
        call_count = 0

        @retry_with_backoff(max_retries=2, initial_delay=0.1)
        def always_fail_func() -> Never:
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_fail_func()

        assert call_count == 3  # Initial attempt + 2 retries

    @staticmethod
    def test_retry_respects_exception_filter() -> None:
        """Test retry decorator only catches specified exceptions."""

        @retry_with_backoff(max_retries=2, initial_delay=0.1, exceptions=(ValueError,))
        def specific_exception_func() -> Never:
            raise TypeError("Wrong exception type")

        with pytest.raises(TypeError, match="Wrong exception type"):
            specific_exception_func()
