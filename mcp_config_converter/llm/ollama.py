"""Local Ollama LLM provider."""

from typing import Any

try:
    import ollama
except ImportError:
    ollama = None

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.llm.base import BaseLLMProvider


@ProviderRegistry.register_provider("ollama")
class OllamaProvider(BaseLLMProvider):
    """Local Ollama LLM provider."""

    PROVIDER_NAME = "ollama"
    ENV_VAR_API_KEY = None  # No API key required
    DEFAULT_MODEL = "llama2"
    REQUIRES_API_KEY = False

    def __init__(self, model: str | None = None, base_url: str = "http://localhost:11434", **kwargs: Any):
        """Initialize Ollama provider.

        Args:
            model: Model to use
            base_url: Ollama API base URL
            **kwargs: Additional arguments
        """
        super().__init__(model=model, **kwargs)
        self.base_url = base_url
        self._client = None

    def _create_client(self) -> Any:
        """Create Ollama client."""
        try:
            return ollama
        except Exception:
            return None

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text using Ollama.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self._client is None:
            self._client = self._create_client()
            if self._client is None:
                raise RuntimeError("Ollama client not available")

        response = self._client.generate(model=self.model, prompt=prompt, stream=False)
        return response.get("response", "")
