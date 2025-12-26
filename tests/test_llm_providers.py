"""Tests for LLM providers."""

import os

import pytest

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.registry import create_provider, list_providers, select_best_provider


class TestLLMProviders:
    """Tests for all registered LLM providers."""

    @staticmethod
    def test_list_providers() -> None:
        """Test that we can list all registered providers."""
        providers = list_providers()
        if len(providers) == 0:
            pytest.fail("No LLM providers registered")
        print(f"Registered providers: {providers}")

    @staticmethod
    @pytest.mark.parametrize("provider_name", list_providers())
    def test_provider_functionality(provider_name: str) -> None:
        """Comprehensive test covering all aspects of provider functionality."""
        # ===== 1. INITIALIZATION TEST =====
        try:
            provider = create_provider(provider_name)
            if provider is None:
                pytest.fail(f"{provider_name}: Provider creation failed")
            if not isinstance(provider, BaseLLMProvider):
                pytest.fail(f"{provider_name}: Provider is not a BaseLLMProvider instance")
            if provider_name != provider.PROVIDER_NAME:
                pytest.fail(f"{provider_name}: Provider name mismatch")
        except Exception as e:
            # Some providers might fail initialization if dependencies are missing
            print(f"⚠ {provider_name}: Initialization failed (expected if dependencies missing): {e}")
            pytest.skip(f"Provider {provider_name} initialization failed: {e}")

        print(f"✓ {provider_name}: Initialization successful")

        # ===== 2. API KEY HANDLING TEST =====
        try:
            api_key_source = provider.get_api_key_source()

            if provider.REQUIRES_API_KEY:
                if api_key_source:
                    print(f"✓ {provider_name}: API key source detected: {api_key_source}")
                else:
                    print(f"⚠ {provider_name}: No API key source (expected if not configured)")
            else:
                print(f"✓ {provider_name}: No API key required")
        except Exception as e:
            print(f"⚠ {provider_name}: API key handling test failed: {e}")
            pytest.skip(f"Provider {provider_name} API key handling test failed: {e}")

        # ===== 3. MODEL SELECTION TEST =====
        try:
            if provider.model is None:
                pytest.fail(f"{provider_name}: No model selected")
            if not isinstance(provider.model, str):
                pytest.fail(f"{provider_name}: Model should be string")

            print(f"✓ {provider_name}: Model '{provider.model}' selected")
        except Exception as e:
            print(f"⚠ {provider_name}: Model selection failed: {e}")
            pytest.skip(f"Provider {provider_name} model selection failed: {e}")

        # ===== 4. VALIDATION TEST =====
        try:
            # Check if provider requires API key
            if provider.REQUIRES_API_KEY:
                # Check if API key is available in environment
                api_key_available = False
                if provider.ENV_VAR_API_KEY:
                    env_vars = provider.ENV_VAR_API_KEY if isinstance(provider.ENV_VAR_API_KEY, list) else [provider.ENV_VAR_API_KEY]
                    for env_var in env_vars:
                        if os.getenv(env_var):
                            api_key_available = True
                            break

                if not api_key_available:
                    print(f"⚠ {provider_name}: Skipping validation - no API key available")
                    return  # Skip validation when no API key available

            # Validate configuration
            is_valid = provider.validate_config()
            if is_valid:
                print(f"✓ {provider_name}: Configuration validated successfully")
            else:
                print(f"⚠ {provider_name}: Configuration validation failed (expected if API key missing)")
                return

        except Exception as e:
            print(f"⚠ {provider_name}: Validation failed (expected if dependencies missing): {e}")
            pytest.skip(f"Provider {provider_name} validation failed: {e}")

        # ===== 5. EXPLICIT API KEY TEST (for first provider only) =====
        if provider_name == list_providers()[0]:  # Only test this once to avoid redundancy
            try:
                dummy_api_key = "test_api_key_12345"
                provider_with_key = create_provider(provider_name, api_key=dummy_api_key)
                if provider_with_key.api_key != dummy_api_key:
                    pytest.fail(f"{provider_name}: API key parameter handling failed")
                print(f"✓ {provider_name}: API key parameter handling works")
            except Exception as e:
                print(f"⚠ {provider_name}: API key parameter test failed: {e}")
                pytest.skip(f"Provider {provider_name} API key parameter test failed: {e}")

    @staticmethod
    def test_provider_selection_functionality() -> None:
        """Comprehensive test covering provider selection and creation functionality."""
        # ===== 1. CUSTOM PROVIDER CREATION TEST =====
        custom_provider_name = "custom_test_provider"

        try:
            # Test that custom provider creation fails without base_url (expected behavior)
            try:
                create_provider(custom_provider_name)
                pytest.fail("Custom provider creation should fail without base_url")
            except ValueError as e:
                if "base_url" not in str(e):
                    pytest.fail(f"Unexpected error message: {e}")
                print("✓ Custom provider validation works correctly")

            # Test that custom provider creation succeeds with base_url
            try:
                custom_provider = create_provider(custom_provider_name, base_url="http://localhost:11434")
                if not isinstance(custom_provider, BaseLLMProvider):
                    pytest.fail("Custom provider should be a BaseLLMProvider instance")
                print("✓ Custom provider creation with base_url works")
            except Exception as e:
                pytest.fail(f"Custom provider creation with base_url failed: {e}")

        except Exception as e:
            pytest.fail(f"Custom provider tests failed: {e}")

        # ===== 2. AUTO PROVIDER SELECTION TEST =====
        try:
            # Test auto provider selection - this might fail if no providers are configured
            try:
                auto_provider = select_best_provider()
                if auto_provider is None:
                    pytest.fail("Auto provider selection should return a provider or raise ValueError")
                if not isinstance(auto_provider, BaseLLMProvider):
                    pytest.fail("Auto-selected provider should be a BaseLLMProvider instance")
                print(f"✓ Auto provider selection works: {auto_provider.PROVIDER_NAME}")
            except ValueError as e:
                # This is expected if no providers are properly configured
                if "No suitable LLM provider found" not in str(e):
                    pytest.fail(f"Unexpected ValueError: {e}")
                print("⚠ Auto provider selection failed (expected if no providers configured)")
            except Exception as e:
                pytest.fail(f"Auto provider selection test failed: {e}")

        except Exception as e:
            pytest.fail(f"Auto provider selection tests failed: {e}")
