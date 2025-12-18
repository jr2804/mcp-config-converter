"""OpenRouter LLM provider using proprietary SDK."""

import functools
from typing import Any

try:
    from openrouter import OpenRouter as OpenRouterClient
except ImportError:
    OpenRouterClient = None

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.registry import register_provider


@register_provider("openrouter", cost=18)
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

    def _get_client(self) -> Any:
        """Create OpenRouter client."""
        if OpenRouterClient is None:
            raise RuntimeError("OpenRouter client not available")

        if not self.api_key:
            raise RuntimeError("OpenRouter client requires API key")

        if self._client is None:
            self._client = OpenRouterClient(api_key=self.api_key)

        return self._client

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """Generate text using OpenRouter SDK.

        Args:
            prompt: Input prompt
            system_prompt: Optional system instruction that guides generation
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._get_client().chat.send(model=self.model, messages=messages, **kwargs)
        return response.choices[0].message.content or ""

    @functools.cached_property
    def available_models(self) -> list[str] | None:
        """Get the list of available models for this provider.

        Returns:
            List of available model names, or None if not available
        """
        try:
            response = self._get_client().models.list()
            return [model.id for model in response.data]
        except Exception:
            return None
