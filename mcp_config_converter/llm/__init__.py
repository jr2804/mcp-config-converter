"""LLM providers for AI-assisted configuration conversion."""

import logging

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
from .registry import (
    ProviderInfo,
    auto_discover,
    create_provider,
    get_provider,
    get_provider_info,
    list_providers,
    register_provider,
    select_best_provider,
)
from .sambanova import SambaNovaOpenAIProvider, SambaNovaSDKProvider

logger = logging.getLogger(__name__)

# Auto-discover providers on import
auto_discover()

__all__ = [
    "BaseLLMProvider",
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
    "SambaNovaOpenAIProvider",
    "SambaNovaSDKProvider",
    "auto_discover",
    "create_provider",
    "get_provider",
    "get_provider_info",
    "list_providers",
    "register_provider",
    "select_best_provider",
]
