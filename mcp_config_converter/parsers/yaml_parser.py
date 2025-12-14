"""YAML parser for MCP configurations."""

from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

from mcp_config_converter.models import MCPConfig
from mcp_config_converter.parsers.base import BaseParser


class YAMLParser(BaseParser):
    """Parser for YAML configuration files."""

    def parse(self, content: str | bytes) -> MCPConfig:
        """Parse YAML content into MCPConfig model.

        Args:
            content: YAML content as string or bytes

        Returns:
            MCPConfig: Parsed configuration

        Raises:
            ImportError: If PyYAML is not installed
        """
        if yaml is None:
            raise ImportError("PyYAML is required for YAML parsing. Install with: pip install pyyaml")

        if isinstance(content, bytes):
            content = content.decode("utf-8")

        data = yaml.safe_load(content)
        return MCPConfig(**data)

    def parse_file(self, file_path: Path) -> MCPConfig:
        """Parse YAML file into MCPConfig model.

        Args:
            file_path: Path to YAML file

        Returns:
            MCPConfig: Parsed configuration
        """
        with open(file_path) as f:
            return self.parse(f.read())
