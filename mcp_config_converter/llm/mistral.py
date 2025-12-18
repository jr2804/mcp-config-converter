"""Mistral AI LLM provider."""

import functools
from typing import Any

try:
    from mistralai import Mistral
    from mistralai.models import UserMessage
except ImportError:
    Mistral = None

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.registry import register_provider


@register_provider("mistral", cost=25)
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

    def _get_client(self) -> Any:
        """Create Mistral client."""
        if Mistral is None:
            raise RuntimeError("Mistral client not available")

        if self._client is None:
            self._client = Mistral(api_key=self.api_key) if self.api_key else Mistral()

        return self._client

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """Generate text using Mistral.

        Args:
            prompt: Input prompt
            system_prompt: Optional system instruction that guides generation
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        max_tokens = kwargs.get("max_tokens", 1024)

        messages: list[UserMessage] = []
        if system_prompt:
            messages.append(UserMessage(role="system", content=system_prompt))
        messages.append(UserMessage(role="user", content=prompt))
        chat_response = self._get_client().chat.complete(model=self.model, messages=messages, max_tokens=max_tokens)

        return chat_response.choices[0].message.content or ""

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
