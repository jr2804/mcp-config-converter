"""OpenAI compatible LLM provider."""

import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from mcp_config_converter.llm.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI compatible LLM provider."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4-turbo", base_url: str | None = None, **kwargs):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use
            base_url: Base URL for custom endpoints
            **kwargs: Additional arguments
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")

        super().__init__(api_key=api_key, **kwargs)
        self.model = model
        self.base_url = base_url
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        if OpenAI is None:
            raise ImportError("openai is required. Install with: pip install openai")

        if self.api_key:
            if self.base_url:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            else:
                self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = OpenAI()

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self.client is None:
            raise RuntimeError("Client not initialized")

        max_tokens = kwargs.get("max_tokens", 1024)

        response = self.client.chat.completions.create(model=self.model, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}])

        return response.choices[0].message.content or ""

    def validate_config(self) -> bool:
        """Validate OpenAI configuration.

        Returns:
            True if configuration is valid
        """
        return self.client is not None and (self.api_key is not None or os.getenv("OPENAI_API_KEY") is not None)
