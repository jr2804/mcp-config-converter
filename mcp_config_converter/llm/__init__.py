"""LLM client for AI-assisted configuration conversion."""

import logging

from .client import (
    PROVIDER_API_KEY_ENV_VARS,
    PROVIDER_COST_FACTORS,
    PROVIDER_DEFAULT_MODELS,
    LiteLLMClient,
    create_client_from_env,
    detect_available_providers,
    get_provider_cost,
    get_providers_sorted_by_cost,
)

logger = logging.getLogger(__name__)

__all__ = [
    "PROVIDER_API_KEY_ENV_VARS",
    "PROVIDER_COST_FACTORS",
    "PROVIDER_DEFAULT_MODELS",
    "LiteLLMClient",
    "create_client_from_env",
    "detect_available_providers",
    "get_provider_cost",
    "get_providers_sorted_by_cost",
]
