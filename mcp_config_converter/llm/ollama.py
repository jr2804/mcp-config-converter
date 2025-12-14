"""Local Ollama LLM provider."""


try:
    import ollama
except ImportError:
    ollama = None

from mcp_config_converter.llm.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Local Ollama LLM provider."""

    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434", **kwargs):
        """Initialize Ollama provider.

        Args:
            model: Model to use
            base_url: Ollama API base URL
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if ollama is None:
            raise ImportError("ollama is required. Install with: pip install ollama")

        response = ollama.generate(model=self.model, prompt=prompt, stream=False)

        return response.get("response", "")

    def validate_config(self) -> bool:
        """Validate Ollama configuration.

        Returns:
            True if configuration is valid
        """
        if ollama is None:
            return False

        try:
            # Try to list models to validate connection
            models = ollama.list()
            return bool(models)
        except Exception:
            return False
