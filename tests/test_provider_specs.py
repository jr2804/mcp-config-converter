"""Test provider specification loading functionality."""

import pytest

from mcp_config_converter.prompts.conversion import _get_provider_specification


class TestProviderSpecifications:
    """Test provider specification loading functionality."""

    @staticmethod
    @pytest.mark.parametrize("provider", ["claude", "vscode", "gemini", "mistral", "opencode"])
    def test_get_provider_specification_returns_markdown(provider: str) -> None:
        """Test that _get_provider_specification returns valid markdown content."""
        spec_content = _get_provider_specification(target_provider=provider)

        # Verify it's non-empty markdown content
        if not spec_content.strip():
            raise AssertionError(f"Provider {provider} specification should not be empty")
        if not isinstance(spec_content, str):
            raise AssertionError(f"Provider {provider} specification should be a string")

        # Basic markdown format validation
        if "# " not in spec_content:
            raise AssertionError(f"Provider {provider} specification should contain markdown headers")

    @staticmethod
    def test_get_provider_specification_invalid_provider() -> None:
        """Test that invalid providers raise appropriate exceptions."""
        with pytest.raises(FileNotFoundError, match="Required specification file not found"):
            _get_provider_specification(target_provider="nonexistent")

    @staticmethod
    def test_all_provider_specs_exist() -> None:
        """Test that all expected provider specification files exist."""
        expected_providers = ["claude", "vscode", "gemini", "mistral", "opencode"]
        for provider in expected_providers:
            # If this doesn't raise an exception, the spec file exists
            spec_content = _get_provider_specification(target_provider=provider)
            if not spec_content.strip():
                raise AssertionError(f"Provider {provider} specification should not be empty")
