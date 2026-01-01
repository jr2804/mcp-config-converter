"""LLM providers for AI-assisted configuration conversion."""

import logging

from .base import BaseLLMProvider
from .litellm_provider import LiteLLMProvider
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

logger = logging.getLogger(__name__)

# Auto-discover providers on import
auto_discover()

__all__ = [
    "BaseLLMProvider",
    "LiteLLMProvider",
    "ProviderInfo",
    "auto_discover",
    "create_provider",
    "get_provider",
    "get_provider_info",
    "list_providers",
    "register_provider",
    "select_best_provider",
]
