"""Abstract base formatter for MCP configurations."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from mcp_config_converter.models import MCPConfig


class BaseFormatter(ABC):
    """Abstract base class for configuration formatters."""

    @abstractmethod
    def format(self, config: MCPConfig) -> str:
        """Format MCPConfig into provider-specific format.

        Args:
            config: MCPConfig to format

        Returns:
            Formatted configuration string
        """
        pass

    @abstractmethod
    def format_dict(self, config: MCPConfig) -> Dict[str, Any]:
        """Format MCPConfig into provider-specific dictionary structure.

        Args:
            config: MCPConfig to format

        Returns:
            Formatted configuration as dictionary
        """
        pass
