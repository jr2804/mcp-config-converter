"""OpenRouter LLM provider using proprietary SDK."""

import os

try:
    from openrouter import OpenRouter as OpenRouterClient
except ImportError:
    OpenRouterClient = None

from mcp_config_converter.llm.base import BaseLLMProvider


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter LLM provider using proprietary SDK."""

    def __init__(self, api_key: str | None = None, model: str = "openai/gpt-4", **kwargs):
        """Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            model: Model to use (default: openai/gpt-4)
            **kwargs: Additional arguments
        """
        if api_key is None:
            api_key = os.getenv("OPENROUTER_API_KEY")

        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize OpenRouter client."""
        if OpenRouterClient is None:
            raise ImportError("openrouter is required. Install with: pip install openrouter")

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

        # Initialize OpenRouter client
        self.client = OpenRouterClient(api_key=self.api_key)

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenRouter SDK.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self.client is None:
            raise RuntimeError("Client not initialized")

        # Use OpenRouter SDK for generation
        response = self.client.chat.send(model=self.model, messages=[{"role": "user", "content": prompt}], **kwargs)

        return response.choices[0].message.content or ""

    def validate_config(self) -> bool:
        """Validate OpenRouter configuration.

        Returns:
            True if configuration is valid
        """
        if OpenRouterClient is None:
            return False

        if not self.api_key and not os.getenv("OPENROUTER_API_KEY"):
            return False

        return self.client is not None
