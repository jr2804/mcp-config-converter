"""Anthropic Claude LLM provider."""

from typing import Any

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.registry import register_provider


@register_provider("claude", cost=20)
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

    def _get_client(self) -> Any:
        """Create Anthropic client."""
        if Anthropic is None:
            raise RuntimeError("Anthropic client not available")

        if self._client is None:
            self._client = Anthropic(api_key=self.api_key) if self.api_key else Anthropic()

        return self._client

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """Generate text using Claude.

        Args:
            prompt: Input prompt
            system_prompt: Optional system instruction that guides generation
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        max_tokens = kwargs.get("max_tokens", 1024)

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        message = self._get_client().messages.create(model=self.model, max_tokens=max_tokens, messages=messages)

        return message.content[0].text

    @property
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
