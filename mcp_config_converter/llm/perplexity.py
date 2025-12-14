"""Perplexity LLM provider implementations."""

import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from perplexity import Client as PerplexityClient
except ImportError:
    PerplexityClient = None

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.openai import OpenAIProvider


class PerplexityOpenAIProvider(OpenAIProvider):
    """Perplexity LLM provider using OpenAI-compatible API."""

    def __init__(self, api_key: str | None = None, model: str = "llama-3-70b-instruct", base_url: str = "https://api.perplexity.ai", **kwargs):
        """Initialize Perplexity OpenAI-compatible provider.

        Args:
            api_key: Perplexity API key (defaults to PERPLEXITY_API_KEY env var)
            model: Model to use (default: llama-3-70b-instruct)
            base_url: Perplexity API base URL
            **kwargs: Additional arguments
        """
        if api_key is None:
            api_key = os.getenv("PERPLEXITY_API_KEY")

        super().__init__(api_key=api_key, model=model, base_url=base_url, **kwargs)

    def validate_config(self) -> bool:
        """Validate Perplexity OpenAI configuration.

        Returns:
            True if configuration is valid
        """
        # Check if OpenAI is available
        if OpenAI is None:
            return False

        # Check API key
        if not self.api_key and not os.getenv("PERPLEXITY_API_KEY"):
            return False

        # Check client initialization
        return self.client is not None


class PerplexitySDKProvider(BaseLLMProvider):
    """Perplexity LLM provider using proprietary SDK."""

    def __init__(self, api_key: str | None = None, model: str = "llama-3-70b-instruct", **kwargs):
        """Initialize Perplexity SDK provider.

        Args:
            api_key: Perplexity API key (defaults to PERPLEXITY_API_KEY env var)
            model: Model to use (default: llama-3-70b-instruct)
            **kwargs: Additional arguments
        """
        if api_key is None:
            api_key = os.getenv("PERPLEXITY_API_KEY")

        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Perplexity SDK client."""
        if PerplexityClient is None:
            raise ImportError("perplexity is required. Install with: pip install perplexity")

        if not self.api_key:
            raise ValueError("Perplexity API key is required")

        # Initialize Perplexity client
        self.client = PerplexityClient(api_key=self.api_key)

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Perplexity SDK.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self.client is None:
            raise RuntimeError("Client not initialized")

        # Use Perplexity SDK for generation
        response = self.client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}], **kwargs)

        return response.choices[0].message.content or ""

    def validate_config(self) -> bool:
        """Validate Perplexity SDK configuration.

        Returns:
            True if configuration is valid
        """
        if PerplexityClient is None:
            return False

        if not self.api_key and not os.getenv("PERPLEXITY_API_KEY"):
            return False

        return self.client is not None
