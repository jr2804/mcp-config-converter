"""Abstract base class for LLM providers."""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    # Class variables for provider metadata
    PROVIDER_NAME: ClassVar[str]
    ENV_VAR_API_KEY: ClassVar[str | list[str] | None] = None
    DEFAULT_MODEL: ClassVar[str | None] = None
    REQUIRES_API_KEY: ClassVar[bool] = True

    def __init__(self, api_key: str | None = None, model: str | None = None, **kwargs: Any):
        """Initialize LLM provider.

        Args:
            api_key: API key for the provider
            model: Model to use (if None, will try to auto-select from available models)
            **kwargs: Additional provider-specific arguments
        """
        self.api_key = self._get_api_key(api_key)

        # Determine the model to use
        if model is not None:
            self.model = model
        elif self.DEFAULT_MODEL is not None:
            self.model = self.DEFAULT_MODEL
        else:
            # Try to select the last available model
            self.model = self._select_last_available_model()

        self.kwargs = kwargs
        self._client = None

        logger.debug(f"Initializing {self.PROVIDER_NAME} provider with model: {self.model}")
        if self.api_key:
            logger.debug(f"Using API key from {self.get_api_key_source()}")

    def _select_last_available_model(self) -> str:
        """Select the last model from available_models list.

        Returns:
            The last available model, or 'default' if no models are available
        """
        try:
            # Create a temporary client to get available models
            if models := self.available_models:
                last_model = models[-1]
                logger.debug(f"Auto-selected last available model: {last_model}")
                return last_model

            # Fallback to default if we can't get models or no models available
            logger.debug("No available models found, using 'default'")
            return "default"
        except Exception as e:
            logger.debug(f"Error selecting last available model: {e}, falling back to 'default'")
            return "default"

    def _get_api_key(self, api_key: str | None) -> str | None:
        """Get API key from parameter or environment variable(s).

        Args:
            api_key: API key provided as parameter

        Returns:
            API key from parameter or first available environment variable
        """
        if api_key is not None:
            return api_key.strip() if isinstance(api_key, str) else api_key

        if self.ENV_VAR_API_KEY is None:
            return None

        env_vars = self.ENV_VAR_API_KEY if isinstance(self.ENV_VAR_API_KEY, list) else [self.ENV_VAR_API_KEY]

        for env_var in env_vars:
            value = os.getenv(env_var)
            if value and value.strip():  # Check for non-empty value
                logger.debug(f"Found API key in {env_var}")
                return value.strip()

        return None

    def get_api_key_source(self) -> str | None:
        """Get the source of the API key.

        Returns:
            Source of the API key or None if not available
        """
        if self.api_key is None:
            return None

        if self.ENV_VAR_API_KEY is None:
            return "parameter"

        env_vars = self.ENV_VAR_API_KEY if isinstance(self.ENV_VAR_API_KEY, list) else [self.ENV_VAR_API_KEY]

        for env_var in env_vars:
            if os.getenv(env_var) == self.api_key:
                return env_var

        return "parameter"

    @abstractmethod
    def _get_client(self) -> Any:
        """Return/Create the client instance."""
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate text from a prompt.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        pass

    @property
    def available_models(self) -> list[str] | None:
        """Get the list of available models for this provider.

        Returns:
            List of available model names, or None if not available
        """
        return None

    def validate_config(self) -> bool:
        """Validate provider configuration.

        Returns:
            True if configuration is valid
        """
        if self.REQUIRES_API_KEY and not self.api_key:
            logger.debug(f"{self.PROVIDER_NAME}: No API key available")
            return False

        try:
            client = self._get_client()
            if client is None:
                logger.debug(f"{self.PROVIDER_NAME}: Client creation failed")
                return False
        except Exception as e:
            logger.debug(f"{self.PROVIDER_NAME}: Validation error: {e}")
            return False

        # Check if the selected model is in available models (if available)
        if self.available_models is not None and self.model not in self.available_models:
            logger.warning(f"{self.PROVIDER_NAME}: Model '{self.model}' not found in available models")
            return False

        return True
