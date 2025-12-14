"""Anthropic Claude LLM provider."""

from typing import Any

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.base import BaseLLMProvider


@ProviderRegistry.register_provider("claude")
class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""

    PROVIDER_NAME = "claude"
    ENV_VAR_API_KEY = "ANTHROPIC_API_KEY"
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize Claude provider.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use
            **kwargs: Additional arguments
        """
        super().__init__(api_key=api_key, model=model, **kwargs)
        self._client = None

    def _create_client(self) -> Any:
        """Create Anthropic client."""
        try:
            if Anthropic is None:
                return None

            if self.api_key:
                return Anthropic(api_key=self.api_key)
            return Anthropic()
        except Exception:
            return None

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using Claude.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self._client is None:
            self._client = self._create_client()
            if self._client is None:
                raise RuntimeError("Anthropic client not available")

        max_tokens = kwargs.get("max_tokens", 1024)

        message = self._client.messages.create(model=self.model, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}])

        return message.content[0].text
