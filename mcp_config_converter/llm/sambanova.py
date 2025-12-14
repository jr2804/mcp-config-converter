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


@ProviderRegistry.register_provider("sambanova-openai")
class SambaNovaOpenAIProvider(BaseLLMProvider):
    """SambaNova LLM provider using OpenAI-compatible API."""

    PROVIDER_NAME = "sambanova-openai"
    ENV_VAR_API_KEY = "SAMBANOVA_API_KEY"
    DEFAULT_MODEL = "Meta-Llama-3.3-70B-Instruct"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None, **kwargs: Any):
        """Initialize SambaNova OpenAI-compatible provider.

        Args:
            api_key: SambaNova API key (defaults to SAMBANOVA_API_KEY env var)
            model: Model to use (default: Meta-Llama-3.3-70B-Instruct)
            base_url: SambaNova API base URL (required for SambaCloud/SambaStack)
            **kwargs: Additional arguments
        """
        if base_url is None:
            raise ValueError("SambaNova requires base_url to be specified")

        super().__init__(api_key=api_key, model=model, **kwargs)
        self.base_url = base_url
        self._client = None

    def _create_client(self) -> Any:
        """Create SambaNova OpenAI client."""
        try:
            if OpenAI is None:
                return None

            if self.api_key:
                return OpenAI(api_key=self.api_key, base_url=self.base_url)
            return OpenAI(base_url=self.base_url)
        except Exception:
            return None

    def validate_config(self) -> bool:
        """Validate SambaNova OpenAI configuration.

        Returns:
            True if configuration is valid
        """
        if OpenAI is None:
            return False

        if not self.api_key and not os.getenv("SAMBANOVA_API_KEY"):
            return False

        if not self.base_url:
            return False

        return self._client is not None


@ProviderRegistry.register_provider("sambanova-sdk")
class SambaNovaSDKProvider(BaseLLMProvider):
    """SambaNova LLM provider using proprietary SDK."""

    PROVIDER_NAME = "sambanova-sdk"
    ENV_VAR_API_KEY = "SAMBANOVA_API_KEY"
    DEFAULT_MODEL = "Meta-Llama-3.3-70B-Instruct"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None, **kwargs: Any):
        """Initialize SambaNova SDK provider.

        Args:
            api_key: SambaNova API key (defaults to SAMBANOVA_API_KEY env var)
            model: Model to use (default: Meta-Llama-3.3-70B-Instruct)
            base_url: SambaNova API base URL (required)
            **kwargs: Additional arguments
        """
        if base_url is None:
            raise ValueError("SambaNova SDK requires base_url to be specified")

        super().__init__(api_key=api_key, model=model, **kwargs)
        self.base_url = base_url
        self._client = None

    def _create_client(self) -> Any:
        """Create SambaNova SDK client."""
        try:
            if sambanova is None:
                return None

            if not self.api_key:
                return None

            return sambanova.Client(base_url=self.base_url, api_key=self.api_key)
        except Exception:
            return None

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using SambaNova SDK.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self._client is None:
            self._client = self._create_client()
            if self._client is None:
                raise RuntimeError("SambaNova SDK client not available")

        response = self._client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}], **kwargs)
        return response.choices[0].message.content or ""
