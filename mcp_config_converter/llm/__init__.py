"""LLM providers for AI-assisted configuration conversion."""

import importlib
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Provider registry
_PROVIDER_REGISTRY: dict[str, type["BaseLLMProvider"]] = {}


class ProviderRegistry:
    """Registry for LLM providers with auto-discovery."""

    @classmethod
    def register_provider(cls, provider_name: str) -> Any:
        """Decorator to register LLM providers."""

        def decorator(provider_class: type["BaseLLMProvider"]):
            _PROVIDER_REGISTRY[provider_name] = provider_class
            logger.debug(f"Registered provider: {provider_name}")
            return provider_class

        return decorator

    @classmethod
    def get_provider(cls, provider_name: str) -> type["BaseLLMProvider"]:
        """Get provider class by name."""
        return _PROVIDER_REGISTRY.get(provider_name)

    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered providers."""
        return list(_PROVIDER_REGISTRY.keys())

    @classmethod
    def create_provider(cls, provider_name: str, **kwargs: Any) -> "BaseLLMProvider":
        """Create provider instance by name."""
        provider_class = cls.get_provider(provider_name)
        if provider_class is None:
            raise ValueError(f"Provider {provider_name} not found")
        return provider_class(**kwargs)

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
    "ProviderRegistry",
    "SambaNovaOpenAIProvider",
    "SambaNovaSDKProvider",
]
