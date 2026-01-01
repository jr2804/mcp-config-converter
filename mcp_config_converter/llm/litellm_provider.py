"""Unified LiteLLM provider implementation."""

import logging
import os
import time
from typing import Any

from litellm import completion
from litellm.exceptions import (
    APIConnectionError,
    RateLimitError,
    ServiceUnavailableError,
)

from mcp_config_converter.llm.base import BaseLLMProvider
from mcp_config_converter.llm.registry import register_provider

logger = logging.getLogger(__name__)


# Model mapping configuration: friendly names to LiteLLM model identifiers
MODEL_MAPPINGS = {
    # OpenAI models
    "gpt-4": "gpt-4",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-4-turbo": "gpt-4-turbo",
    "gpt-4o": "gpt-4o",
    "gpt-oss-20b": "gpt-4o-mini",
    "gpt-oss-120b": "gpt-4o",
    # Anthropic Claude models
    "claude-3-opus-20240229": "claude-3-opus-20240229",
    "claude-3-sonnet-20240229": "claude-3-sonnet-20240229",
    "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022",
    "claude-3-haiku-20240307": "claude-3-haiku-20240307",
    # Google Gemini models
    "gemini-pro": "gemini/gemini-pro",
    "gemini-2.5-flash": "gemini/gemini-2.0-flash-exp",
    "gemini-1.5-pro": "gemini/gemini-1.5-pro",
    "gemini-1.5-flash": "gemini/gemini-1.5-flash",
    # Ollama models
    "ollama/llama2": "ollama/llama2",
    "ollama/mistral": "ollama/mistral",
    "ollama/codellama": "ollama/codellama",
    # Mistral models
    "mistral-small": "mistral/mistral-small-latest",
    "mistral-medium": "mistral/mistral-medium-latest",
    "mistral-large": "mistral/mistral-large-latest",
    "mistral-medium-latest": "mistral/mistral-medium-latest",
    # DeepSeek models
    "deepseek-chat": "deepseek/deepseek-chat",
    "deepseek-coder": "deepseek/deepseek-coder",
    # OpenRouter models
    "openai/gpt-4": "openrouter/openai/gpt-4",
    "openai/gpt-3.5-turbo": "openrouter/openai/gpt-3.5-turbo",
    # Perplexity models
    "sonar": "perplexity/sonar",
    "sonar-pro": "perplexity/sonar-pro",
    # SambaNova models
    "samba-1": "sambanova/Meta-Llama-3.1-8B-Instruct",
    "samba-2": "sambanova/Meta-Llama-3.1-70B-Instruct",
    # ZAI models
    "glm-4.7": "glm-4",
    "glm-4": "glm-4",
}

# Environment variable mappings for different providers
PROVIDER_ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY"],
    "google": ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY"],
    "mistral": "MISTRAL_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
    "sambanova": "SAMBANOVA_API_KEY",
    "zai": "ZAI_API_KEY",
    "ollama": None,  # No API key required
}


@register_provider("litellm", cost=5)
class LiteLLMProvider(BaseLLMProvider):
    """Unified LiteLLM provider for all supported LLM APIs."""

    PROVIDER_NAME = "litellm"
    ENV_VAR_API_KEY = None  # Determined dynamically based on model
    DEFAULT_MODEL = "gpt-4o-mini"
    REQUIRES_API_KEY = False  # Determined dynamically based on model

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs: Any,
    ):
        """Initialize LiteLLM provider.

        Args:
            api_key: API key for the provider
            model: Model to use (supports friendly names from MODEL_MAPPINGS)
            base_url: Base URL for custom endpoints
            max_retries: Maximum number of retry attempts for rate limits
            retry_delay: Initial delay between retries (exponential backoff)
            **kwargs: Additional provider-specific arguments
        """
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Map friendly model name to LiteLLM identifier
        if model and model in MODEL_MAPPINGS:
            self._litellm_model = MODEL_MAPPINGS[model]
        else:
            self._litellm_model = model

        super().__init__(api_key=api_key, model=model, **kwargs)

        # Determine if API key is required based on model
        if self.model:
            self.REQUIRES_API_KEY = not self._is_local_model(self.model)

        logger.debug(f"Initialized LiteLLM provider with model: {self.model} -> {self._litellm_model}")

    def _is_local_model(self, model: str) -> bool:
        """Check if the model is a local model (e.g., Ollama)."""
        return model.startswith("ollama/") or model.startswith("ollama_")

    def _get_api_key_for_model(self, model: str) -> str | None:
        """Get API key based on the model being used."""
        if self.api_key:
            return self.api_key

        # Determine provider from model name
        if model.startswith("gpt-") or model.startswith("openai/"):
            env_vars = ["OPENAI_API_KEY"]
        elif model.startswith("claude-") or model.startswith("anthropic/"):
            env_vars = ["ANTHROPIC_API_KEY"]
        elif model.startswith("gemini/") or "gemini" in model.lower():
            env_vars = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY"]
        elif model.startswith("mistral/"):
            env_vars = ["MISTRAL_API_KEY"]
        elif model.startswith("deepseek/"):
            env_vars = ["DEEPSEEK_API_KEY"]
        elif model.startswith("openrouter/"):
            env_vars = ["OPENROUTER_API_KEY"]
        elif model.startswith("perplexity/"):
            env_vars = ["PERPLEXITY_API_KEY"]
        elif model.startswith("sambanova/"):
            env_vars = ["SAMBANOVA_API_KEY"]
        elif "glm-" in model.lower():
            env_vars = ["ZAI_API_KEY"]
        elif model.startswith("ollama/"):
            return None  # No API key needed for Ollama
        else:
            env_vars = ["OPENAI_API_KEY"]  # Default fallback

        # Try each environment variable
        for env_var in env_vars:
            value = os.getenv(env_var)
            if value and value.strip():
                logger.debug(f"Found API key in {env_var} for model {model}")
                return value.strip()

        return None

    def _get_client(self) -> Any:
        """LiteLLM doesn't require a persistent client, returns None."""
        return None

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """Generate text using LiteLLM.

        Args:
            prompt: Input prompt
            system_prompt: Optional system instruction that guides generation
            **kwargs: Additional generation parameters

        Returns:
            Generated text

        Raises:
            RuntimeError: If generation fails after all retries
        """
        max_tokens = kwargs.get("max_tokens", 1024)

        # Build messages array
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Get API key for this model
        api_key = self._get_api_key_for_model(self._litellm_model or self.model)

        # Prepare completion parameters
        completion_kwargs: dict[str, Any] = {
            "model": self._litellm_model or self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

        if api_key:
            completion_kwargs["api_key"] = api_key

        if self.base_url:
            completion_kwargs["api_base"] = self.base_url

        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in ["max_tokens"]:
                completion_kwargs[key] = value

        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = completion(**completion_kwargs)
                return response.choices[0].message.content or ""
            except (RateLimitError, ServiceUnavailableError, APIConnectionError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during generation: {e}")
                raise RuntimeError(f"LiteLLM generation failed: {e}") from e

        raise RuntimeError(f"LiteLLM generation failed after {self.max_retries} retries: {last_exception}") from last_exception

    @property
    def available_models(self) -> list[str] | None:
        """Get the list of available models.

        Returns:
            List of friendly model names from MODEL_MAPPINGS
        """
        return list(MODEL_MAPPINGS.keys())

    def validate_config(self) -> bool:
        """Validate provider configuration.

        Returns:
            True if configuration is valid
        """
        if not self.model:
            logger.debug("LiteLLM: No model specified")
            return False

        # Check if model requires API key
        if self.REQUIRES_API_KEY:
            api_key = self._get_api_key_for_model(self._litellm_model or self.model)
            if not api_key:
                logger.debug(f"LiteLLM: No API key available for model {self.model}")
                return False

        return True
