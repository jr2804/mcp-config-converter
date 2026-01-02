"""Simplified LiteLLM client wrapper for MCP Config Converter."""

import logging
import os
import time
from typing import Any

from litellm import completion, model_list
from litellm.exceptions import (
    APIConnectionError,
    RateLimitError,
    ServiceUnavailableError,
)

logger = logging.getLogger(__name__)


# Provider-specific default models  
PROVIDER_DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-sonnet-20241022",
    "gemini": "gemini-2.0-flash-exp",
    "vertex_ai": "gemini-2.0-flash-exp",
    "ollama": "llama2",
    "mistral": "mistral-medium-latest",
    "deepseek": "deepseek-chat",
    "openrouter": "openai/gpt-4",
    "perplexity": "sonar",
    "sambanova": "Meta-Llama-3.1-8B-Instruct",
    "cohere": "command",
}

# Environment variable mappings for different providers
PROVIDER_API_KEY_ENV_VARS = {
    "openai": ["OPENAI_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY"],
    "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY"],
    "vertex_ai": ["VERTEX_AI_PROJECT", "GOOGLE_APPLICATION_CREDENTIALS"],
    "mistral": ["MISTRAL_API_KEY"],
    "deepseek": ["DEEPSEEK_API_KEY"],
    "openrouter": ["OPENROUTER_API_KEY"],
    "perplexity": ["PERPLEXITY_API_KEY"],
    "sambanova": ["SAMBANOVA_API_KEY"],
    "cohere": ["COHERE_API_KEY"],
    "ollama": [],  # No API key required
}


class LiteLLMClient:
    """Simplified wrapper around LiteLLM completion API."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        **kwargs: Any,
    ):
        """Initialize LiteLLM client.

        Args:
            provider: Provider type (e.g., 'openai', 'anthropic', 'gemini')
            model: Model name to use
            api_key: API key for the provider
            base_url: Custom base URL for the provider
            max_retries: Maximum number of retry attempts for rate limits
            retry_delay: Initial delay between retries (exponential backoff)
            **kwargs: Additional provider-specific arguments
        """
        self.provider = provider
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.kwargs = kwargs

        # Get API key (provided or from environment)
        self.api_key = api_key or self._get_api_key_from_env()

        # Determine model to use
        if model:
            self.model = model
        elif provider and provider in PROVIDER_DEFAULT_MODELS:
            self.model = PROVIDER_DEFAULT_MODELS[provider]
        else:
            self.model = "gpt-4o-mini"  # Fallback default

        logger.debug(f"Initialized LiteLLM client: provider={self.provider}, model={self.model}")

    def _get_api_key_from_env(self) -> str | None:
        """Get API key from environment variables based on provider."""
        if not self.provider:
            return None

        env_vars = PROVIDER_API_KEY_ENV_VARS.get(self.provider, [])
        for env_var in env_vars:
            value = os.getenv(env_var)
            if value and value.strip():
                logger.debug(f"Found API key in {env_var}")
                return value.strip()

        return None

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """Generate text using LiteLLM.

        Args:
            prompt: Input prompt
            system_prompt: Optional system instruction
            **kwargs: Additional generation parameters (e.g., max_tokens, temperature)

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

        # Prepare completion parameters
        completion_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

        if self.api_key:
            completion_kwargs["api_key"] = self.api_key

        if self.base_url:
            completion_kwargs["api_base"] = self.base_url

        # Add any additional kwargs
        for key, value in kwargs.items():
            if key not in ["max_tokens"]:
                completion_kwargs[key] = value

        # Add provider-specific kwargs
        for key, value in self.kwargs.items():
            if key not in completion_kwargs:
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
                logger.error(f"Unexpected error during generation (type: {type(e).__name__}): {e}")
                raise RuntimeError(f"LiteLLM generation failed: {e}") from e

        raise RuntimeError(f"LiteLLM generation failed after {self.max_retries} retries: {last_exception}") from last_exception

    def get_available_models(self) -> list[str]:
        """Get list of available models for this provider.

        Returns:
            List of model names available through LiteLLM
        """
        try:
            # Use LiteLLM's model_list to get available models
            models = model_list()
            if self.provider:
                # Filter models for this provider if specified
                # LiteLLM model names often start with provider prefix
                filtered = [m for m in models if m.startswith(f"{self.provider}/") or "/" not in m]
                return filtered if filtered else models
            return models
        except Exception as e:
            logger.debug(f"Could not get model list: {e}")
            return []

    def validate_config(self) -> bool:
        """Validate client configuration.

        Returns:
            True if configuration appears valid
        """
        # Check if model is set
        if not self.model:
            logger.debug("No model specified")
            return False

        # Check if API key is available for providers that need it
        if self.provider and self.provider not in ["ollama"]:
            if not self.api_key:
                logger.debug(f"No API key available for provider {self.provider}")
                return False

        return True


def detect_available_providers() -> list[tuple[str, str | None]]:
    """Detect which LLM providers are available based on configured API keys.

    Returns:
        List of tuples (provider_name, api_key) for available providers
    """
    available = []

    for provider, env_vars in PROVIDER_API_KEY_ENV_VARS.items():
        if not env_vars:  # Providers like Ollama that don't need API keys
            available.append((provider, None))
            continue

        for env_var in env_vars:
            value = os.getenv(env_var)
            if value and value.strip():
                available.append((provider, value.strip()))
                break

    return available


def create_client_from_env() -> LiteLLMClient | None:
    """Create a LiteLLM client from environment variables.

    Checks for MCP_CONFIG_CONF_* environment variables first, then auto-detects
    available providers.

    Returns:
        LiteLLMClient instance or None if no configuration found
    """
    # Check for explicit configuration
    provider = os.getenv("MCP_CONFIG_CONF_LLM_PROVIDER_TYPE")
    model = os.getenv("MCP_CONFIG_CONF_LLM_MODEL")
    api_key = os.getenv("MCP_CONFIG_CONF_API_KEY")
    base_url = os.getenv("MCP_CONFIG_CONF_LLM_BASE_URL")

    if provider or model or api_key or base_url:
        logger.debug(f"Creating client from explicit configuration: provider={provider}, model={model}")
        return LiteLLMClient(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
        )

    # Auto-detect available providers
    available = detect_available_providers()
    if available:
        provider_name, api_key = available[0]  # Use first available
        logger.debug(f"Auto-detected provider: {provider_name}")
        return LiteLLMClient(provider=provider_name, api_key=api_key)

    logger.debug("No LiteLLM configuration found")
    return None
