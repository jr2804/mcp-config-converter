"""LLM prompt templates for MCP configuration conversion."""

from mcp_config_converter.prompts.base import BasePromptTemplate, PromptRegistry
from mcp_config_converter.prompts.conversion import MCPConversionPrompt

__all__ = [
    "BasePromptTemplate",
    "MCPConversionPrompt",
    "PromptRegistry",
]
