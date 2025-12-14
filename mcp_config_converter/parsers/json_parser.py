"""JSON parser for MCP configurations."""

import json
from pathlib import Path

from mcp_config_converter.models import MCPConfig
from mcp_config_converter.parsers.base import BaseParser


class JSONParser(BaseParser):
    """Parser for JSON configuration files."""

    def parse(self, content: str | bytes) -> MCPConfig:
        """Parse JSON content into MCPConfig model.

        Args:
            content: JSON content as string or bytes

        Returns:
            MCPConfig: Parsed configuration
        """
        if isinstance(content, bytes):
            content = content.decode("utf-8")

        data = json.loads(content)
        return MCPConfig(**data)

    def parse_file(self, file_path: Path) -> MCPConfig:
        """Parse JSON file into MCPConfig model.

        Args:
            file_path: Path to JSON file

        Returns:
            MCPConfig: Parsed configuration
        """
        with open(file_path) as f:
            return self.parse(f.read())
