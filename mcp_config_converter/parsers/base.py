"""Abstract base parser for MCP configurations."""

from abc import ABC, abstractmethod
from pathlib import Path

from mcp_config_converter.models import MCPConfig


class BaseParser(ABC):
    """Abstract base class for configuration parsers."""

    @abstractmethod
    def parse(self, content: str | bytes) -> MCPConfig:
        """Parse configuration content into MCPConfig model.

        Args:
            content: Configuration content as string or bytes

        Returns:
            MCPConfig: Parsed configuration
        """
        pass

    @abstractmethod
    def parse_file(self, file_path: Path) -> MCPConfig:
        """Parse configuration from file.

        Args:
            file_path: Path to configuration file

        Returns:
            MCPConfig: Parsed configuration
        """
        pass
