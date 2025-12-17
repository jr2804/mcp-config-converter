"""SambaNova LLM provider implementations."""

import functools
import os
from typing import Any

try:
    import sambanova
except ImportError:
    sambanova = None

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.openai import OpenAIProvider


@ProviderRegistry.register_provider("sambanova-openai", cost=16)
class SambaNovaOpenAIProvider(OpenAIProvider):
    """SambaNova LLM provider using OpenAI-compatible API."""

    PROVIDER_NAME = "sambanova-openai"
    ENV_VAR_API_KEY = "SAMBANOVA_API_KEY"
    DEFAULT_MODEL = "gpt-oss-120b"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize SambaNova OpenAI-compatible provider.

        Args:
            api_key: SambaNova API key (defaults to SAMBANOVA_API_KEY env var)
            model: Model to use (default: Meta-Llama-3.3-70B-Instruct)
            base_url: SambaNova API base URL (required for SambaCloud/SambaStack)
            **kwargs: Additional arguments
        """
        base_url = os.getenv("SAMBANOVA_API_BASE_URL", "https://api.sambanova.ai/v1")
        super().__init__(api_key=api_key, model=model, base_url=base_url, **kwargs)


@ProviderRegistry.register_provider("sambanova-sdk", cost=17)
class SambaNovaSDKProvider(BaseLLMProvider):
    """SambaNova LLM provider using proprietary SDK."""

    PROVIDER_NAME = "sambanova-sdk"
    ENV_VAR_API_KEY = "SAMBANOVA_API_KEY"
    DEFAULT_MODEL = "gpt-oss-120b"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize SambaNova SDK provider.

        Args:
            api_key: SambaNova API key (defaults to SAMBANOVA_API_KEY env var)
            model: Model to use (default: Meta-Llama-3.3-70B-Instruct)
            **kwargs: Additional arguments
        """
        super().__init__(api_key=api_key, model=model, **kwargs)

        self.base_url = os.getenv("SAMBANOVA_API_BASE_URL")

    def _get_client(self) -> Any:
        """Create SambaNova SDK client."""
        if sambanova is None:
            raise RuntimeError("SambaNova SDK client not available")

        if not self.api_key:
            raise RuntimeError("SambaNova SDK client requires API key")

        if self._client is None:
            self._client = sambanova.Client(base_url=self.base_url, api_key=self.api_key)

        return self._client

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using SambaNova SDK.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        response = self._get_client().chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}], **kwargs)
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
