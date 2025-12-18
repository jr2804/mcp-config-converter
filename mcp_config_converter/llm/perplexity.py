"""Perplexity LLM provider implementations."""

import os
from typing import Any

try:
    from perplexity import Client as PerplexityClient
except ImportError:
    PerplexityClient = None

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.openai import OpenAIProvider
from mcp_config_converter.llm.registry import register_provider


@register_provider("perplexity-openai", cost=10)
class PerplexityOpenAIProvider(OpenAIProvider):
    """Perplexity LLM provider using OpenAI-compatible API."""

    PROVIDER_NAME = "perplexity-openai"
    ENV_VAR_API_KEY = "PERPLEXITY_API_KEY"
    DEFAULT_MODEL = "sonar"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize Perplexity OpenAI-compatible provider.

        Args:
            api_key: Perplexity API key (defaults to PERPLEXITY_API_KEY env var)
            model: Model to use (default: sonar)
            base_url: Perplexity API base URL
            **kwargs: Additional arguments
        """
        base_url: str = os.getenv("PERPLEXITY_API_BASE_URL", "https://api.perplexity.ai")
        super().__init__(api_key=api_key, model=model, base_url=base_url, **kwargs)

    @property
    def available_models(self) -> list[str] | None:
        """Get the list of available models for this provider.

        Returns:
            List of available model names
        """
        return ["sonar", "sonar-pro", "sonar-reasoning-pro"]


@register_provider("perplexity-sdk", cost=11)
class PerplexitySDKProvider(BaseLLMProvider):
    """Perplexity LLM provider using proprietary SDK."""

    PROVIDER_NAME = "perplexity-sdk"
    ENV_VAR_API_KEY = "PERPLEXITY_API_KEY"
    DEFAULT_MODEL = "sonar"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize Perplexity SDK provider.

        Args:
            api_key: Perplexity API key (defaults to PERPLEXITY_API_KEY env var)
            model: Model to use (default: llama-3-70b-instruct)
            **kwargs: Additional arguments
        """
        super().__init__(api_key=api_key, model=model, **kwargs)

    def _get_client(self) -> Any:
        """Create Perplexity SDK client."""
        if PerplexityClient is None:
            raise RuntimeError("Perplexity SDK client not available")

        if not self.api_key:
            raise RuntimeError("Perplexity SDK client requires API key")

        if self._client is None:
            self._client = PerplexityClient(api_key=self.api_key)

        return self._client

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """Generate text using Perplexity SDK.

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

        response = self._get_client().chat.completions.create(model=self.model, messages=messages, **kwargs)
        return response.choices[0].message.content or ""

    @property
    def available_models(self) -> list[str] | None:
        """Get the list of available models for this provider.

        Returns:
            List of available model names
        """
        return ["sonar", "sonar-pro", "sonar-reasoning-pro"]
