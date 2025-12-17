from __future__ import annotations

import logging
from typing import Any

from mcp_config_converter.llm import create_provider, list_providers
from mcp_config_converter.llm.claude import ClaudeProvider
from mcp_config_converter.llm.openai import OpenAIProvider

logger = logging.getLogger(__name__)


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
        return create_provider(
            provider_type,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
    except ValueError as e:
        logger.debug(f"Registry creation failed for {provider_type}: {e}")

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

    # Fallback for dynamic custom providers if not registered but args provided
    if base_url:
        try:
            # Assuming OpenAI compatible for custom base_url
            return OpenAIProvider(api_key=api_key, model=model or "default-model", base_url=base_url)
        except Exception as e:
            logger.debug(f"Custom provider creation failed: {e}")

    raise ValueError(f"Unknown provider type: {provider_type}. Available providers: {', '.join(list_providers())}")
