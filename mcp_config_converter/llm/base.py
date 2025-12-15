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
            model: Model to use
            **kwargs: Additional provider-specific arguments
        """
        self.api_key = self._get_api_key(api_key)
        self.model = model or self.DEFAULT_MODEL
        self.kwargs = kwargs

        logger.debug(f"Initializing {self.PROVIDER_NAME} provider")
        if self.api_key:
            logger.debug(f"Using API key from {self.get_api_key_source()}")

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
    def _create_client(self) -> Any:
        """Create the client instance."""
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

    def validate_config(self) -> bool:
        """Validate provider configuration.

        Returns:
            True if configuration is valid
        """
        if self.REQUIRES_API_KEY and not self.api_key:
            logger.debug(f"{self.PROVIDER_NAME}: No API key available")
            return False

        try:
            client = self._create_client()
            if client is None:
                logger.debug(f"{self.PROVIDER_NAME}: Client creation failed")
                return False
            return True
        except Exception as e:
            logger.debug(f"{self.PROVIDER_NAME}: Validation error: {e}")
            return False
