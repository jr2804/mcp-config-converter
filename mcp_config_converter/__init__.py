"""MCP Config Converter - Convert MCP configurations between formats and LLM providers."""

from importlib.metadata import PackageNotFoundError

from mcp_config_converter.transformers import ConfigTransformer

try:
    # default: from metadata
    from importlib.metadata import version

    __version__ = version(__name__)
except (ImportError, PackageNotFoundError):
    # dynamic: from _version
    from mcp_config_converter._version import version as __version__


__author__ = "jr2804"

__all__ = ["ConfigTransformer", "__version__"]
