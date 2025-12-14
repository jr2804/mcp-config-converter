"""SambaNova LLM provider implementations."""

import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import sambanova
except ImportError:
    sambanova = None

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.openai import OpenAIProvider


class SambaNovaOpenAIProvider(OpenAIProvider):
    """SambaNova LLM provider using OpenAI-compatible API."""

    def __init__(self, api_key: str | None = None, model: str = "Meta-Llama-3.3-70B-Instruct", base_url: str | None = None, **kwargs):
        """Initialize SambaNova OpenAI-compatible provider.

        Args:
            api_key: SambaNova API key (defaults to SAMBANOVA_API_KEY env var)
            model: Model to use (default: Meta-Llama-3.3-70B-Instruct)
            base_url: SambaNova API base URL (required for SambaCloud/SambaStack)
            **kwargs: Additional arguments
        """
        if api_key is None:
            api_key = os.getenv("SAMBANOVA_API_KEY")

        # SambaNova requires explicit base_url
        if base_url is None:
            raise ValueError("SambaNova requires base_url to be specified")

        super().__init__(api_key=api_key, model=model, base_url=base_url, **kwargs)

    def validate_config(self) -> bool:
        """Validate SambaNova OpenAI configuration.

        Returns:
            True if configuration is valid
        """
        # Check if OpenAI is available
        if OpenAI is None:
            return False

        # Check API key
        if not self.api_key and not os.getenv("SAMBANOVA_API_KEY"):
            return False

        # Check base URL
        if not self.base_url:
            return False

        # Check client initialization
        return self.client is not None


class SambaNovaSDKProvider(BaseLLMProvider):
    """SambaNova LLM provider using proprietary SDK."""

    def __init__(self, api_key: str | None = None, model: str = "Meta-Llama-3.3-70B-Instruct", base_url: str | None = None, **kwargs):
        """Initialize SambaNova SDK provider.

        Args:
            api_key: SambaNova API key (defaults to SAMBANOVA_API_KEY env var)
            model: Model to use (default: Meta-Llama-3.3-70B-Instruct)
            base_url: SambaNova API base URL (required)
            **kwargs: Additional arguments
        """
        if api_key is None:
            api_key = os.getenv("SAMBANOVA_API_KEY")

        if base_url is None:
            raise ValueError("SambaNova SDK requires base_url to be specified")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.kwargs = kwargs
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize SambaNova SDK client."""
        if sambanova is None:
            raise ImportError("sambanova is required. Install with: pip install sambanova")

        if not self.api_key:
            raise ValueError("SambaNova API key is required")

        if not self.base_url:
            raise ValueError("SambaNova base_url is required")

        # Initialize SambaNova client
        self.client = sambanova.Client(base_url=self.base_url, api_key=self.api_key)

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using SambaNova SDK.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self.client is None:
            raise RuntimeError("Client not initialized")

        # Use SambaNova SDK for generation
        response = self.client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}], **kwargs)

        return response.choices[0].message.content or ""

    def validate_config(self) -> bool:
        """Validate SambaNova SDK configuration.

        Returns:
            True if configuration is valid
        """
        if sambanova is None:
            return False

        if not self.api_key and not os.getenv("SAMBANOVA_API_KEY"):
            return False

        if not self.base_url:
            return False

        return self.client is not None
