from __future__ import annotations

import logging
from typing import Any

from mcp_config_converter.llm import create_provider, list_providers

logger = logging.getLogger(__name__)


def create_llm_provider(
    provider_type: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> Any | None:
    """Create an LLM provider based on configuration.

    Args:
        provider_type: LLM provider type ('litellm', 'openai', 'anthropic', or specific provider name)
        base_url: Custom base URL for the provider
        api_key: API key for the provider
        model: Model name to use

    Returns:
        An instance of BaseLLMProvider or None if no provider specified

    Raises:
        ValueError: If provider_type is invalid or configuration is incomplete
    """
    if not provider_type:
        return None

    provider_type = provider_type.lower()

    # Map legacy provider type names to litellm for backward compatibility
    if provider_type in ("openai", "anthropic"):
        logger.debug(f"Mapping legacy provider type '{provider_type}' to 'litellm'")
        provider_type = "litellm"

    try:
        return create_provider(
            provider_type,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
    except ValueError as e:
        logger.debug(f"Provider creation failed for {provider_type}: {e}")
        raise ValueError(f"Unknown provider type: {provider_type}. Available providers: {', '.join(list_providers())}")

