"""DeepSeek LLM provider using OpenAI-compatible API."""

from typing import Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.base import BaseLLMProvider


@ProviderRegistry.register_provider("deepseek")
class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek LLM provider using OpenAI-compatible API."""

    PROVIDER_NAME = "deepseek"
    ENV_VAR_API_KEY = "DEEPSEEK_API_KEY"
    DEFAULT_MODEL = "deepseek-chat"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str = "https://api.deepseek.com", **kwargs: Any):
        """Initialize DeepSeek provider.

        Args:
            api_key: DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)
            model: Model to use (default: deepseek-chat)
            base_url: DeepSeek API base URL (default: https://api.deepseek.com)
            **kwargs: Additional arguments
        """
        super().__init__(api_key=api_key, model=model, **kwargs)
        self.base_url = base_url
        self._client = None

    def _create_client(self) -> Any:
        """Create DeepSeek client."""
        try:
            if OpenAI is None:
                return None

            if self.api_key:
                return OpenAI(api_key=self.api_key, base_url=self.base_url)
            return OpenAI(base_url=self.base_url)
        except Exception:
            return None
