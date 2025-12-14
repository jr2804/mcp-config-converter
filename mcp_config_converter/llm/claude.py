"""Anthropic Claude LLM provider."""

import os

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from mcp_config_converter.llm.base import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        """Initialize Claude provider.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use
            **kwargs: Additional arguments
        """
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")

        super().__init__(api_key=api_key, **kwargs)
        self.model = model
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Anthropic client."""
        if Anthropic is None:
            raise ImportError("anthropic is required. Install with: pip install anthropic")

        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            self.client = Anthropic()

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Claude.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self.client is None:
            raise RuntimeError("Client not initialized")

        max_tokens = kwargs.get("max_tokens", 1024)

        message = self.client.messages.create(model=self.model, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}])

        return message.content[0].text

    def validate_config(self) -> bool:
        """Validate Claude configuration.

        Returns:
            True if configuration is valid
        """
        return self.client is not None and (self.api_key is not None or os.getenv("ANTHROPIC_API_KEY") is not None)
