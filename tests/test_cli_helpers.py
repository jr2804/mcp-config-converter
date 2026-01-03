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
        if not validate_format_choice("claude"):
            raise AssertionError("validate_format_choice('claude') should return True")
        if not validate_format_choice("gemini"):
            raise AssertionError("validate_format_choice('gemini') should return True")
        if not validate_format_choice("vscode"):
            raise AssertionError("validate_format_choice('vscode') should return True")

    @staticmethod
    def test_validate_format_choice_invalid() -> None:
        """Test format validation with invalid choices."""
        if validate_format_choice("json"):
            raise AssertionError("validate_format_choice('json') should return False")
        if validate_format_choice("invalid"):
            raise AssertionError("validate_format_choice('invalid') should return False")
        if validate_format_choice(""):
            raise AssertionError("validate_format_choice('') should return False")

    @staticmethod
    def test_validate_provider_choice_valid() -> None:
        """Test provider validation with valid choices."""
        if not validate_provider_choice("claude"):
            raise AssertionError("validate_provider_choice('claude') should return True")
        if not validate_provider_choice("gemini"):
            raise AssertionError("validate_provider_choice('gemini') should return True")
        if not validate_provider_choice("mistral"):
            raise AssertionError("validate_provider_choice('mistral') should return True")
        if not validate_provider_choice("vscode"):
            raise AssertionError("validate_provider_choice('vscode') should return True")
        if not validate_provider_choice("opencode"):
            raise AssertionError("validate_provider_choice('opencode') should return True")

    @staticmethod
    def test_validate_provider_choice_invalid() -> None:
        """Test provider validation with invalid choices."""
        if validate_provider_choice("openai"):
            raise AssertionError("validate_provider_choice('openai') should return False")
        if validate_provider_choice("invalid"):
            raise AssertionError("validate_provider_choice('invalid') should return False")
        if validate_provider_choice(""):
            raise AssertionError("validate_provider_choice('') should return False")


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
        if result != "success":
            raise AssertionError(f"Expected 'success', got {result!r}")
        if call_count != 1:
            raise AssertionError(f"Expected call_count=1, got {call_count}")

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
        if result != "success":
            raise AssertionError(f"Expected 'success', got {result!r}")
        if call_count != 3:
            raise AssertionError(f"Expected call_count=3, got {call_count}")

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

        if call_count != 3:  # Initial attempt + 2 retries
            raise AssertionError(f"Expected call_count=3, got {call_count}")

    @staticmethod
    def test_retry_respects_exception_filter() -> None:
        """Test retry decorator only catches specified exceptions."""

        @retry_with_backoff(max_retries=2, initial_delay=0.1, exceptions=(ValueError,))
        def specific_exception_func() -> Never:
            raise TypeError("Wrong exception type")

        with pytest.raises(TypeError, match="Wrong exception type"):
            specific_exception_func()
