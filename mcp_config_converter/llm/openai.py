"""OpenAI compatible LLM provider."""

from typing import Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.base import BaseLLMProvider


@ProviderRegistry.register_provider("openai")
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
        self._client = None

    def _create_client(self) -> Any:
        """Create OpenAI client."""
        try:
            if OpenAI is None:
                return None

            if self.api_key:
                if self.base_url:
                    return OpenAI(api_key=self.api_key, base_url=self.base_url)
                return OpenAI(api_key=self.api_key)

            # a valid OpenAI client needs at least an api_key
            return None
        except Exception:
            return None

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using OpenAI.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self._client is None:
            self._client = self._create_client()
            if self._client is None:
                raise RuntimeError("OpenAI client not available")

        max_tokens = kwargs.get("max_tokens", 1024)

        response = self._client.chat.completions.create(model=self.model, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}])

        return response.choices[0].message.content or ""
