"""OpenAI compatible LLM provider."""

from typing import Any

from openai import OpenAI

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.registry import register_provider


@register_provider("openai", cost=15)
class OpenAIProvider(BaseLLMProvider):
    """OpenAI compatible LLM provider."""

    PROVIDER_NAME = "openai"
    ENV_VAR_API_KEY = "OPENAI_API_KEY"
    DEFAULT_MODEL = "gpt-oss-20b"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None, **kwargs: Any):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use
            base_url: Base URL for custom endpoints
            **kwargs: Additional arguments
        """
        # Ensure base_url is not in kwargs to avoid duplicate parameter error
        kwargs.pop("base_url", None)
        super().__init__(api_key=api_key, model=model, **kwargs)
        self.base_url = base_url

    def _get_client(self) -> Any:
        """Create OpenAI client."""
        if not self.api_key:
            raise RuntimeError("OpenAI client requires API key")

        if self._client is None:
            if self.base_url:
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            else:
                self._client = OpenAI(api_key=self.api_key)

        return self._client

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using OpenAI.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        max_tokens = kwargs.get("max_tokens", 1024)

        response = self._get_client().chat.completions.create(model=self.model, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}])

        return response.choices[0].message.content or ""

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
