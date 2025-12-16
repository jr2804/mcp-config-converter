"""LLM providers for AI-assisted configuration conversion."""

import importlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Provider registry
_PROVIDER_REGISTRY: dict[str, "ProviderInfo"] = {}


@dataclass(frozen=True)
class ProviderInfo:
    """Provider registration information."""

    provider_class: type["BaseLLMProvider"]
    cost: int = 10


class ProviderRegistry:
    """Registry for LLM providers with auto-discovery."""

    @classmethod
    def register_provider(cls, provider_name: str, cost: int = 10) -> Any:
        """Decorator to register LLM providers.

        Args:
            provider_name: Name of provider
            cost: Cost value for auto-selection (default: 10)

        Returns:
            Decorator function
        """

        def decorator(provider_class: type["BaseLLMProvider"]) -> type["BaseLLMProvider"]:
            _PROVIDER_REGISTRY[provider_name] = ProviderInfo(provider_class=provider_class, cost=cost)
            logger.debug(f"Registered provider: {provider_name} (cost: {cost})")
            return provider_class

        return decorator

    @classmethod
    def get_provider_info(cls, provider_name: str) -> ProviderInfo | None:
        """Get provider info by name."""
        return _PROVIDER_REGISTRY.get(provider_name)

    @classmethod
    def get_provider(cls, provider_name: str) -> type["BaseLLMProvider"] | None:
        """Get provider class by name."""
        provider_info = _PROVIDER_REGISTRY.get(provider_name)
        return provider_info.provider_class if provider_info else None

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered providers."""
        return list(_PROVIDER_REGISTRY.keys())

    @classmethod
    def create_provider(cls, provider_name: str, **kwargs: Any) -> "BaseLLMProvider":
        """Create provider instance by name.

        Args:
            provider_name: Name of provider or "auto"
            **kwargs: Additional provider-specific arguments

        Returns:
            Provider instance

        Raises:
            ValueError: If provider not found or auto-selection fails
        """
        if provider_name == "auto":
            return cls.select_best_provider(**kwargs)

        provider_info = cls.get_provider_info(provider_name)
        if provider_info is None:
            # Try to create a custom provider if not registered
            return cls._create_custom_provider(provider_name, **kwargs)

        return provider_info.provider_class(**kwargs)

    @classmethod
    def select_best_provider(cls, **kwargs: Any) -> "BaseLLMProvider":
        """Select the best available provider based on cost and availability.

        Args:
            **kwargs: Additional provider-specific arguments

        Returns:
            Provider instance

        Raises:
            ValueError: If no suitable provider is found
        """
        # Sort providers by cost (ascending)
        sorted_providers = sorted(_PROVIDER_REGISTRY.items(), key=lambda item: item[1].cost)

        for provider_name, provider_info in sorted_providers:
            try:
                provider = provider_info.provider_class(**kwargs)
                if provider.validate_config():
                    logger.debug(f"Selected provider: {provider_name} (cost: {provider_info.cost})")
                    return provider
                else:
                    logger.debug(f"Provider {provider_name} is not properly configured")
            except Exception as e:
                logger.debug(f"Failed to initialize provider {provider_name}: {e}")

        raise ValueError("No suitable LLM provider found and properly configured")

    @classmethod
    def _create_custom_provider(cls, provider_name: str, **kwargs: Any) -> "BaseLLMProvider":
        """Create a custom provider instance.

        Args:
            provider_name: Provider name (not in registry)
            **kwargs: Provider arguments including base_url

        Returns:
            Provider instance

        Raises:
            ValueError: If required parameters are missing
        """
        if "base_url" not in kwargs:
            raise ValueError(f"Provider '{provider_name}' not found and no base_url provided for custom provider")

        from .openai import OpenAIProvider  # Use OpenAI as base for custom providers

        # Create a custom provider class with the given name
        class CustomProvider(OpenAIProvider):
            PROVIDER_NAME = provider_name

        return CustomProvider(**kwargs)

    @classmethod
    def auto_discover(cls) -> None:
        """Auto-discover providers in the llm directory."""
        llm_dir = Path(__file__).parent

        # Import all modules in the llm directory
        for module_file in llm_dir.glob("*.py"):
            if module_file.name.startswith("_"):
                continue

            module_name = module_file.stem
            if module_name == "__init__":
                continue

            try:
                importlib.import_module(f"mcp_config_converter.llm.{module_name}")
                logger.debug(f"Auto-discovered module: {module_name}")
            except ImportError as e:
                logger.debug(f"Failed to import {module_name}: {e}")


# Auto-discover providers on import
ProviderRegistry.auto_discover()

# Import base class for type hints
from .base import BaseLLMProvider

# Re-export all providers for backward compatibility
from .claude import ClaudeProvider
from .deepseek import DeepSeekProvider
from .gemini import GeminiProvider
from .mistral import MistralProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .openrouter import OpenRouterProvider
from .perplexity import PerplexityOpenAIProvider, PerplexitySDKProvider
from .sambanova import SambaNovaOpenAIProvider, SambaNovaSDKProvider

__all__ = [
    "ClaudeProvider",
    "DeepSeekProvider",
    "GeminiProvider",
    "MistralProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "OpenRouterProvider",
    "PerplexityOpenAIProvider",
    "PerplexitySDKProvider",
    "ProviderInfo",
    "ProviderRegistry",
    "SambaNovaOpenAIProvider",
    "SambaNovaSDKProvider",
]
