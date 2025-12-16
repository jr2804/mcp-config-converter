"""Test provider specification loading functionality."""

import pytest

from mcp_config_converter.prompts.conversion import _get_provider_specification


class TestProviderSpecifications:
    """Test provider specification loading functionality."""

    @pytest.mark.parametrize("provider", ["claude", "vscode", "gemini", "mistral", "opencode"])
    def test_get_provider_specification_returns_markdown(self, provider) -> None:
        """Test that _get_provider_specification returns valid markdown content."""
        spec_content = _get_provider_specification(target_provider=provider)

        # Verify it's non-empty markdown content
        assert spec_content.strip(), f"Provider {provider} specification should not be empty"
        assert isinstance(spec_content, str), f"Provider {provider} specification should be a string"

        # Basic markdown format validation
        assert "# " in spec_content, f"Provider {provider} specification should contain markdown headers"

    def test_get_provider_specification_invalid_provider(self) -> None:
        """Test that invalid providers raise appropriate exceptions."""
        with pytest.raises(FileNotFoundError, match="Required specification file not found"):
            _get_provider_specification(target_provider="nonexistent")

    def test_all_provider_specs_exist(self) -> None:
        """Test that all expected provider specification files exist."""
        expected_providers = ["claude", "vscode", "gemini", "mistral", "opencode"]
        for provider in expected_providers:
            # If this doesn't raise an exception, the spec file exists
            spec_content = _get_provider_specification(target_provider=provider)
            assert spec_content.strip(), f"Provider {provider} specification should not be empty"
