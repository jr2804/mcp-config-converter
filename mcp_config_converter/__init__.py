"""MCP Config Converter - Convert MCP configurations between formats and LLM providers."""

__version__ = "0.1.0"
__author__ = "jr2804"

from mcp_config_converter.models import MCPConfig
from mcp_config_converter.transformers import ConfigTransformer

__all__ = ["ConfigTransformer", "MCPConfig", "__version__"]
