from __future__ import annotations

from typing import Any

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.openai import OpenAIProvider
from mcp_config_converter.llm.claude import ClaudeProvider


def create_llm_provider(
    provider_type: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> Any | None:
    """Create an LLM provider based on configuration.

    Args:
        provider_type: LLM provider type ('openai', 'anthropic', or specific provider name)
        base_url: Custom base URL for the provider
        api_key: API key for the provider
        model: Model name to use

    Returns:
        An instance of BaseLLMProvider or None if no provider specified

    Raises:
        ValueError: If provider_type is invalid or configuration is incomplete
        ImportError: If required dependencies are not installed
    """
    if not provider_type:
        return None

    provider_type = provider_type.lower()

    try:
        return ProviderRegistry.create_provider(
            provider_type,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
    except ValueError:
        pass

    if provider_type == "openai":
        try:
            return OpenAIProvider(
                api_key=api_key,
                model=model or "gpt-4-turbo",
                base_url=base_url,
            )
        except ImportError as e:
            raise ImportError(f"OpenAI provider requires 'openai' package: {e}")

    if provider_type == "anthropic":
        try:
            return ClaudeProvider(
                api_key=api_key,
                model=model or "claude-3-5-sonnet-20241022",
            )
        except ImportError as e:
            raise ImportError(f"Anthropic provider requires 'anthropic' package: {e}")

    raise ValueError(f"Unknown provider type: {provider_type}. Available providers: {', '.join(ProviderRegistry.list_providers())}")
