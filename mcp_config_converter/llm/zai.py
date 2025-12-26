"""Z.AI LLM provider implementations."""

import os
from typing import Any

try:
    from zai import ZaiClient
except ImportError:
    ZaiClient = None

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.openai import OpenAIProvider
from mcp_config_converter.llm.registry import register_provider

# Available Z.AI models (hardcoded from documentation)
# Source: https://docs.z.ai/api-reference/llm/chat-completion
ZAI_MODELS = [
    # Text models
    "glm-4.7",  # Latest flagship model (default)
    "glm-4.6",
    "glm-4.5",
    "glm-4.5-air",
    "glm-4.5-x",
    "glm-4.5-airx",
    "glm-4.5-flash",
    "glm-4-32b-0414-128k",
    # Vision models
    "glm-4.6v",
    "glm-4.5v",
]


@register_provider("zai-openai", cost=18)
class ZaiOpenAIProvider(OpenAIProvider):
    """Z.AI LLM provider using OpenAI-compatible API."""

    PROVIDER_NAME = "zai-openai"
    ENV_VAR_API_KEY = "ZAI_API_KEY"
    DEFAULT_MODEL = "glm-4.7"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize Z.AI OpenAI-compatible provider.

        Args:
            api_key: Z.AI API key (defaults to ZAI_API_KEY env var)
            model: Model to use (default: glm-4.7)
            base_url: Z.AI API base URL
            **kwargs: Additional arguments
        """
        base_url: str = os.getenv("ZAI_API_BASE_URL", "https://api.z.ai/api/paas/v4/")
        super().__init__(api_key=api_key, model=model, base_url=base_url, **kwargs)

    @property
    def available_models(self) -> list[str] | None:
        """Get the list of available models for this provider.

        Returns:
            List of available model names (hardcoded)
        """
        return ZAI_MODELS.copy()


@register_provider("zai-sdk", cost=19)
class ZaiSDKProvider(BaseLLMProvider):
    """Z.AI LLM provider using proprietary SDK."""

    PROVIDER_NAME = "zai-sdk"
    ENV_VAR_API_KEY = "ZAI_API_KEY"
    DEFAULT_MODEL = "glm-4.7"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize Z.AI SDK provider.

        Args:
            api_key: Z.AI API key (defaults to ZAI_API_KEY env var)
            model: Model to use (default: glm-4.7)
            **kwargs: Additional arguments
        """
        super().__init__(api_key=api_key, model=model, **kwargs)

    def _get_client(self) -> Any:
        """Create Z.AI SDK client."""
        if ZaiClient is None:
            raise RuntimeError("Z.AI SDK client not available")

        if not self.api_key:
            raise RuntimeError("Z.AI SDK client requires API key")

        if self._client is None:
            self._client = ZaiClient(api_key=self.api_key)

        return self._client

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """Generate text using Z.AI SDK.

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
            List of available model names (hardcoded)
        """
        return ZAI_MODELS.copy()
