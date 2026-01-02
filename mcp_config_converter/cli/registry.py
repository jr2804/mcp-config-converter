from __future__ import annotations

import logging

from mcp_config_converter.llm import LiteLLMClient, detect_available_providers

logger = logging.getLogger(__name__)


def create_llm_client(
    provider: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> LiteLLMClient | None:
    """Create a LiteLLM client based on configuration.

    Args:
        provider: LiteLLM provider type (e.g., 'openai', 'anthropic', 'gemini')
                 See https://docs.litellm.ai/docs/providers for supported providers
        base_url: Custom base URL for the provider
        api_key: API key for the provider
        model: Model name to use

    Returns:
        LiteLLMClient instance or None if no configuration provided

    Raises:
        ValueError: If configuration is incomplete
    """
    if not any([provider, model, api_key, base_url]):
        return None

    # If no provider specified but other params given, try to auto-detect
    if not provider and (api_key or model):
        available = detect_available_providers()
        if available:
            provider = available[0][0]
            logger.debug(f"Auto-detected provider: {provider}")

    logger.debug(f"Creating LiteLLM client: provider={provider}, model={model}")
    return LiteLLMClient(
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
    )

