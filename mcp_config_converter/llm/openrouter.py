"""OpenRouter LLM provider using proprietary SDK."""

from typing import Any

try:
    from openrouter import OpenRouter as OpenRouterClient
except ImportError:
    OpenRouterClient = None

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.base import BaseLLMProvider


@ProviderRegistry.register_provider("openrouter")
class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter LLM provider using proprietary SDK."""

    PROVIDER_NAME = "openrouter"
    ENV_VAR_API_KEY = "OPENROUTER_API_KEY"
    DEFAULT_MODEL = "openai/gpt-4"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            model: Model to use (default: openai/gpt-4)
            **kwargs: Additional arguments
        """
        super().__init__(api_key=api_key, model=model, **kwargs)
        self._client = None

    def _create_client(self) -> Any:
        """Create OpenRouter client."""
        try:
            if OpenRouterClient is None:
                return None

            if not self.api_key:
                return None

            return OpenRouterClient(api_key=self.api_key)
        except Exception:
            return None

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using OpenRouter SDK.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self._client is None:
            self._client = self._create_client()
            if self._client is None:
                raise RuntimeError("OpenRouter client not available")

        response = self._client.chat.send(model=self.model, messages=[{"role": "user", "content": prompt}], **kwargs)
        return response.choices[0].message.content or ""
