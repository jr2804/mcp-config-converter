"""Simplified LiteLLM client wrapper for MCP Config Converter."""

import logging
import os
import time
from typing import Any

from litellm import completion, get_valid_models
from litellm.caching.caching import Cache
from litellm.exceptions import (
    APIConnectionError,
    RateLimitError,
    ServiceUnavailableError,
)

logger = logging.getLogger(__name__)

# Environment variable name constants to avoid circular import
MCP_CONFIG_CONF_LLM_PROVIDER = "MCP_CONFIG_CONF_LLM_PROVIDER"
MCP_CONFIG_CONF_LLM_MODEL = "MCP_CONFIG_CONF_LLM_MODEL"
MCP_CONFIG_CONF_API_KEY = "MCP_CONFIG_CONF_API_KEY"
MCP_CONFIG_CONF_LLM_BASE_URL = "MCP_CONFIG_CONF_LLM_BASE_URL"
MCP_CONFIG_CONF_LLM_CACHE_ENABLED = "MCP_CONFIG_CONF_LLM_CACHE_ENABLED"
MCP_CONFIG_CONF_LLM_CHECK_PROVIDER_ENDPOINT = "MCP_CONFIG_CONF_LLM_CHECK_PROVIDER_ENDPOINT"


# Provider-specific default models
PROVIDER_DEFAULT_MODELS: dict[str, str | int] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-sonnet-20241022",
    "gemini": "gemini-3-flash-preview",
    "vertex_ai": "gemini-2.0-flash-exp",
    "ollama": 0,  # Use first available model from Ollama
    "mistral": "mistral-medium-latest",
    "deepseek": "deepseek-chat",
    "openrouter": "xiaomi/mimo-v2-flash:free",
    "perplexity": "sonar",
    "poe": "gemini-2.5-flash-lite",
    "sambanova": "Meta-Llama-3.1-8B-Instruct",
    "cohere": "command",
    "zai": "glm-4.7",
}

# Provider cost factors (0-100, lower is cheaper)
# Estimates based on typical pricing per 1M tokens
PROVIDER_COST_FACTORS: dict[str, int] = {
    "ollama": 0,
    "zai": 15,
    "deepseek": 20,
    "openrouter": 25,
    "sambanova": 30,
    "perplexity": 50,
    "gemini": 55,
    "mistral": 60,
    "poe": 65,
    "cohere": 80,
    "openai": 90,
    "anthropic": 95,
    "vertex_ai": 100,
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
    "poe": ["POE_API_KEY"],
    "sambanova": ["SAMBANOVA_API_KEY"],
    "cohere": ["COHERE_API_KEY"],
    "ollama": [],  # No API key required
    "zai": ["ZAI_API_KEY"],
}


class LiteLLMClient:
    """Simplified wrapper around LiteLLM completion API."""

    def __init__(
        self,
        provider: str,
        model: str | int,
        api_key: str | None = None,
        base_url: str | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        enable_cache: bool | None = None,
        cache_type: str = "disk",
        cache_dir: str | None = None,
        check_provider_endpoint: bool | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.25,
        **kwargs: Any,
    ):
        """Initialize LiteLLM client.

        Args:
            provider: Provider type (e.g., 'openai', 'anthropic', 'gemini')
            model: Model name to use, or integer index into available models list
            api_key: API key for provider
            base_url: Custom base URL for provider
            max_retries: Maximum number of retry attempts for rate limits
            retry_delay: Initial delay between retries (exponential backoff)
            enable_cache: Enable caching for completion calls (None checks env var)
            cache_type: Type of cache to use (default: "disk")
            cache_dir: Directory for disk cache (optional)
            check_provider_endpoint: Query provider endpoints for accurate model lists (None checks env var)
            max_tokens: Maximum tokens to generate (default set in generate method)
            temperature: Default temperature for generation (may not be supported by all providers)
            **kwargs: Additional provider-specific arguments
        """
        self.provider = provider
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.add_model_kwargs = kwargs

        # Handle enable_cache: None means check env var, otherwise use explicit value
        if enable_cache is None:
            self.enable_cache = os.getenv(MCP_CONFIG_CONF_LLM_CACHE_ENABLED, "false").lower() == "true"
        else:
            self.enable_cache = enable_cache

        # Handle check_provider_endpoint: None means check env var, otherwise use explicit value
        if check_provider_endpoint is None:
            self.check_provider_endpoint = os.getenv(MCP_CONFIG_CONF_LLM_CHECK_PROVIDER_ENDPOINT, "false").lower() == "true"
        else:
            self.check_provider_endpoint = check_provider_endpoint

        # Get API key (provided or from environment)
        self.api_key = api_key or self._get_api_key_from_env()

        # Determine model to use
        if model is not None:
            self.model = self._resolve_model(model)
        elif provider and provider in PROVIDER_DEFAULT_MODELS:
            default_model = PROVIDER_DEFAULT_MODELS[provider]
            self.model = self._resolve_model(default_model)
        else:
            raise ValueError(f"No model specified and no default model for provider '{provider}'")

        # Initialize cache if enabled
        if self.enable_cache:
            cache_kwargs: dict[str, Any] = {"type": cache_type}
            if cache_dir:
                cache_kwargs["disk_cache_dir"] = cache_dir
            Cache(**cache_kwargs)
            logger.debug(f"Initialized {cache_type} cache: dir={cache_dir}")

        logger.debug(f"Initialized LiteLLM client: provider={self.provider}, model={self.model}, cache_enabled={self.enable_cache}")

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """Generate text using LiteLLM.

        Args:
            prompt: Input prompt
            system_prompt: Optional system instruction
            **kwargs: Additional generation parameters (e.g., max_tokens, temperature - will override self.add_model_kwargs)

        Returns:
            Generated text

        Raises:
            RuntimeError: If generation fails after all retries
        """
        # Build messages array
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Prepare completion parameters - combine mandatory client params with any overrides
        completion_kwargs: dict[str, Any] = self.add_model_kwargs.copy()
        completion_kwargs.update(
            {
                "model": f"{self.provider}/{self.model}",
                "messages": messages,
                "max_tokens": self.max_tokens,
                "drop_params": True,
                "temperature": self.temperature,
            }
        )

        # do not pass None to completion function
        if self.api_key:
            completion_kwargs["api_key"] = self.api_key

        if self.base_url:
            completion_kwargs["api_base"] = self.base_url

        if self.enable_cache:
            completion_kwargs["caching"] = True

        # Add any additional kwargs
        completion_kwargs.update(kwargs)

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
            # For Ollama, always check the actual endpoint to get installed models
            if self.provider == "ollama":
                models = get_valid_models(check_provider_endpoint=True, custom_llm_provider="ollama")
                # Filter out embedding models (they can't generate text)
                generative_models = [m for m in models if "embed" not in m.lower()]
                return generative_models if generative_models else models

            if self.check_provider_endpoint:
                if self.provider:
                    models = get_valid_models(check_provider_endpoint=True, custom_llm_provider=self.provider)
                else:
                    models = get_valid_models(check_provider_endpoint=True)
            else:
                models = get_valid_models()

            if self.provider:
                filtered = [m for m in models if m.startswith(f"{self.provider}/") or (self.provider in m and "/" not in m)]
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
        if self.provider and self.provider not in ["ollama"] and not self.api_key:
            logger.debug(f"No API key available for provider {self.provider}")
            return False

        return True

    def _resolve_model(self, model: str | int) -> str:
        """Resolve model specification to actual model name.

        If model is an integer, use it as an index into the available models list.
        Supports negative indices (e.g., -1 for last model).
        If model is a string, return it as-is (no provider prefixing).

        Args:
            model: Model name or index

        Returns:
            Resolved model name as string

        Raises:
            ValueError: If index is out of bounds, no models are available, or invalid type
        """
        if isinstance(model, str):
            return model

        if isinstance(model, int):
            available_models = self.get_available_models()
            if not available_models:
                raise ValueError(f"No models available for provider {self.provider}")

            try:
                resolved = available_models[model]
                logger.info(f"Resolved model index {model} to model name: {resolved}")
                return resolved
            except IndexError:
                raise ValueError(
                    f"Model index {model} is out of bounds. "
                    f"Available models: {len(available_models)} "
                    f"(valid indices: {-len(available_models)} to {len(available_models) - 1})"
                )

        raise ValueError(f"Invalid model type: {type(model)}. Expected str or int")

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


def get_providers_sorted_by_cost(providers: list[str] | None = None) -> list[str]:
    """Get available providers sorted by cost (cheapest first).

    Args:
        providers: List of provider names to consider, or None for all

    Returns:
        List of provider names sorted by cost factor (ascending)
    """
    if providers is None:
        providers = list(PROVIDER_COST_FACTORS.keys())

    sorted_providers = sorted(
        providers,
        key=lambda p: get_provider_cost(p),
    )

    logger.debug(f"Providers sorted by cost: {sorted_providers}")
    return sorted_providers


def get_provider_cost(provider: str) -> int:
    """Get cost factor for a provider, checking environment variable overrides.

    Args:
        provider: Provider name (case-insensitive)

    Returns:
        Cost factor as integer (0-100+)

    Raises:
        ValueError: If environment variable is negative or cannot be parsed
    """
    provider_upper = provider.upper()
    env_var_name = f"MCP_CONVERT_CONF_{provider_upper}_COST"
    env_value = os.getenv(env_var_name)

    if env_value is not None:
        try:
            env_cost = int(env_value)
            if env_cost < 0:
                logger.warning(
                    f"Ignored negative cost factor for provider '{provider}': {env_cost}. Using default value: {PROVIDER_COST_FACTORS.get(provider, 0)}"
                )
                return PROVIDER_COST_FACTORS.get(provider, 0)
            return env_cost
        except ValueError:
            logger.warning(f"Invalid cost factor for provider '{provider}': '{env_value}'. Using default value: {PROVIDER_COST_FACTORS.get(provider, 0)}")
            return PROVIDER_COST_FACTORS.get(provider, 0)

    return PROVIDER_COST_FACTORS.get(provider, 0)


def create_client_from_env() -> LiteLLMClient | None:
    """Create a LiteLLM client from environment variables.

    Checks for MCP_CONFIG_CONF_* environment variables first, then auto-detects
    available providers.

    Returns:
        LiteLLMClient instance or None if no configuration found
    """
    # Check for explicit configuration
    provider = os.getenv(MCP_CONFIG_CONF_LLM_PROVIDER)
    model = os.getenv(MCP_CONFIG_CONF_LLM_MODEL)
    api_key = os.getenv(MCP_CONFIG_CONF_API_KEY)
    base_url = os.getenv(MCP_CONFIG_CONF_LLM_BASE_URL)
    enable_cache = os.getenv(MCP_CONFIG_CONF_LLM_CACHE_ENABLED, "false").lower() == "true"
    check_provider_endpoint = os.getenv(MCP_CONFIG_CONF_LLM_CHECK_PROVIDER_ENDPOINT, "false").lower() == "true"

    if provider or model or api_key or base_url:
        logger.debug(f"Creating client from explicit configuration: provider={provider}, model={model}")
        if not provider:
            logger.debug("No provider specified in environment, cannot create client")
            return None
        return LiteLLMClient(
            provider=provider,
            model=model or PROVIDER_DEFAULT_MODELS.get(provider, "gpt-4o-mini"),
            api_key=api_key,
            base_url=base_url,
            enable_cache=enable_cache,
            check_provider_endpoint=check_provider_endpoint,
        )

    # Auto-detect available providers
    available = detect_available_providers()
    if available:
        provider_name, api_key = available[0]  # Use first available
        logger.debug(f"Auto-detected provider: {provider_name}")
        default_model = PROVIDER_DEFAULT_MODELS.get(provider_name, "gpt-4o-mini")
        return LiteLLMClient(
            provider=provider_name,
            model=default_model,
            api_key=api_key,
            enable_cache=enable_cache,
            check_provider_endpoint=check_provider_endpoint,
        )

    logger.debug("No LiteLLM configuration found")
    return None
