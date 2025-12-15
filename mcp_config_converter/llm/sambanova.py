"""SambaNova LLM provider implementations."""

import os
from typing import Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import sambanova
except ImportError:
    sambanova = None

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.openai import OpenAIProvider


@ProviderRegistry.register_provider("sambanova-openai")
class SambaNovaOpenAIProvider(OpenAIProvider):
    """SambaNova LLM provider using OpenAI-compatible API."""

    PROVIDER_NAME = "sambanova-openai"
    ENV_VAR_API_KEY = "SAMBANOVA_API_KEY"
    DEFAULT_MODEL = "gpt-oss-120b-32k"
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


@ProviderRegistry.register_provider("sambanova-sdk")
class SambaNovaSDKProvider(BaseLLMProvider):
    """SambaNova LLM provider using proprietary SDK."""

    PROVIDER_NAME = "sambanova-sdk"
    ENV_VAR_API_KEY = "SAMBANOVA_API_KEY"
    DEFAULT_MODEL = "gpt-oss-120b-32k"
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
        self._client = None

    def _create_client(self) -> Any:
        """Create SambaNova SDK client."""
        if (sambanova is not None) and (self.api_key is not None):
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
        if self._client is None:
            raise RuntimeError("SambaNova SDK client not available")

        response = self._client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}], **kwargs)
        return response.choices[0].message.content or ""
