"""Mistral AI LLM provider."""

from typing import Any

try:
    from mistralai import Mistral
    from mistralai.models import UserMessage
except ImportError:
    Mistral = None

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.base import BaseLLMProvider


@ProviderRegistry.register_provider("mistral", cost=25)
class MistralProvider(BaseLLMProvider):
    """Mistral AI LLM provider."""

    PROVIDER_NAME = "mistral"
    ENV_VAR_API_KEY = "MISTRAL_API_KEY"
    DEFAULT_MODEL = "mistral-medium-latest"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize Mistral provider.

        Args:
            api_key: Mistral API key (defaults to MISTRAL_API_KEY env var)
            model: Model to use
            **kwargs: Additional arguments
        """
        super().__init__(api_key=api_key, model=model, **kwargs)
        self._client = None

    def _create_client(self) -> Any:
        """Create Mistral client."""
        try:
            if Mistral is None:
                return None

            if self.api_key:
                return Mistral(api_key=self.api_key)
            return Mistral()
        except Exception:
            return None

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using Mistral.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self._client is None:
            self._client = self._create_client()
            if self._client is None:
                raise RuntimeError("Mistral client not available")

        max_tokens = kwargs.get("max_tokens", 1024)

        messages = [UserMessage(role="user", content=prompt)]
        chat_response = self._client.chat.complete(model=self.model, messages=messages, max_tokens=max_tokens)

        return chat_response.choices[0].message.content or ""
