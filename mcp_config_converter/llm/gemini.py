"""Google Gemini LLM provider."""

from typing import Any

try:
    import google.generativeai as genai
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
        self._client = None

    def _create_client(self) -> Any:
        """Create Gemini client."""
        try:
            if genai is None:
                return None

            if self.api_key:
                genai.configure(api_key=self.api_key)
                return genai.GenerativeModel(self.model)
            return None
        except Exception:
            return None

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using Gemini.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self._client is None:
            self._client = self._create_client()
            if self._client is None:
                raise RuntimeError("Gemini client not available")

        try:
            response = self._client.generate_content(prompt)
            return response.text or ""
        except Exception:
            return ""
