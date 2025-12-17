"""Google Gemini LLM provider."""

import functools
from typing import Any

try:
    from google import genai
except ImportError:
    genai = None

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.base import BaseLLMProvider


@ProviderRegistry.register_provider("gemini", cost=12)
class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""

    PROVIDER_NAME = "gemini"
    ENV_VAR_API_KEY = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY"]
    DEFAULT_MODEL = "gemini-2.5-flash"
    REQUIRES_API_KEY = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize Gemini provider.

        Args:
            api_key: Google API key (defaults to GEMINI_API_KEY, GOOGLE_API_KEY, or GOOGLE_GENERATIVE_AI_API_KEY env var)
            model: Model to use
            **kwargs: Additional arguments
        """
        super().__init__(api_key=api_key, model=model, **kwargs)

    def _get_client(self) -> Any:
        """Create Gemini client."""
        if genai is None:
            raise RuntimeError("Gemini client not available")

        if self._client is None:
            self._client = genai.Client(api_key=self.api_key) if self.api_key else genai.Client()

        return self._client

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using Gemini.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        response = self._get_client().models.generate_content(model=self.model, contents=prompt)
        return response.text

    @functools.cached_property
    def available_models(self) -> list[str] | None:
        """Get the list of available models for this provider.

        Returns:
            List of available model names, or None if not available
        """
        try:
            models = self._get_client().models.list()
            return [model.name.split("/")[-1] for model in models if (hasattr(model, "name") and model.name)]
        except Exception:
            return None
