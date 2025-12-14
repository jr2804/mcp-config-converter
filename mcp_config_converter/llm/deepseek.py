"""DeepSeek LLM provider using OpenAI-compatible API."""

import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from mcp_config_converter.llm.openai import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek LLM provider using OpenAI-compatible API."""

    def __init__(self, api_key: str | None = None, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com", **kwargs):
        """Initialize DeepSeek provider.

        Args:
            api_key: DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)
            model: Model to use (default: deepseek-chat)
            base_url: DeepSeek API base URL (default: https://api.deepseek.com)
            **kwargs: Additional arguments
        """
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")

        super().__init__(api_key=api_key, model=model, base_url=base_url, **kwargs)

    def validate_config(self) -> bool:
        """Validate DeepSeek configuration.

        Returns:
            True if configuration is valid
        """
        # Check if OpenAI is available
        if OpenAI is None:
            return False

        # Check API key
        if not self.api_key and not os.getenv("DEEPSEEK_API_KEY"):
            return False

        # Check client initialization
        return self.client is not None
