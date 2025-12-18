"""Local Ollama LLM provider."""

import functools
from typing import Any

try:
    from ollama import Client, pull
except ImportError:
    Client = None

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.registry import register_provider


@register_provider("ollama", cost=1)
class OllamaProvider(BaseLLMProvider):
    """Local Ollama LLM provider."""

    PROVIDER_NAME = "ollama"
    ENV_VAR_API_KEY = None  # No API key required
    DEFAULT_MODEL = None
    REQUIRES_API_KEY = False

    def __init__(self, model: str | None = None, base_url: str = "http://localhost:11434", **kwargs: Any):
        """Initialize Ollama provider.

        Args:
            model: Model to use
            base_url: Ollama API base URL
            **kwargs: Additional arguments
        """
        self.base_url = base_url
        super().__init__(model=model, **kwargs)

        if self.model not in self.available_models:
            pull(self.model)

    def _get_client(self) -> Any:
        """Create Ollama client."""
        if Client is None:
            raise RuntimeError("Ollama client not available")

        if self._client is None:
            self._client = Client(host=self.base_url)

        return self._client

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """Generate text using Ollama.

        Args:
            prompt: Input prompt
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        response = self._get_client().generate(model=self.model, prompt=prompt, stream=False, system=system_prompt, **kwargs)
        return response.get("response", "")

    @functools.cached_property
    def available_models(self) -> list[str] | None:
        """Get the list of available models for this provider.

        Returns:
            List of available model names, or None if not available
        """
        try:
            response = self._get_client().list()
            return [model["model"] for model in response["models"]]
        except Exception:
            return None
