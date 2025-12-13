"""Google Gemini LLM provider."""

from typing import Optional
import os

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from mcp_config_converter.llm.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro", **kwargs):
        """Initialize Gemini provider.

        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Model to use
            **kwargs: Additional arguments
        """
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        super().__init__(api_key=api_key, **kwargs)
        self.model = model
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Gemini client."""
        if genai is None:
            raise ImportError("google-generativeai is required. Install with: pip install google-generativeai")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Gemini.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if genai is None:
            raise RuntimeError("google-generativeai not installed")
        
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        
        return response.text

    def validate_config(self) -> bool:
        """Validate Gemini configuration.

        Returns:
            True if configuration is valid
        """
        return self.api_key is not None or os.getenv("GOOGLE_API_KEY") is not None
