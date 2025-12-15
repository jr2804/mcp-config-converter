"""DeepSeek LLM provider using OpenAI-compatible API."""

import os
from typing import Any

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.openai import OpenAIProvider


@ProviderRegistry.register_provider("deepseek")
class DeepSeekProvider(OpenAIProvider):
    """DeepSeek LLM provider using OpenAI-compatible API."""

    PROVIDER_NAME = "deepseek"
    ENV_VAR_API_KEY = "DEEPSEEK_API_KEY"
    DEFAULT_MODEL = "deepseek-chat"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize DeepSeek provider.

        Args:
            api_key: DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)
            model: Model to use (default: deepseek-chat)
            base_url: DeepSeek API base URL (default: https://api.deepseek.com)
            **kwargs: Additional arguments
        """
        base_url = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
        super().__init__(api_key=api_key, model=model, base_url=base_url, **kwargs)
