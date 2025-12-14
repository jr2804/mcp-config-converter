"""TOML parser for MCP configurations."""

from pathlib import Path

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None

try:
    import toml
except ImportError:
    toml = None

from mcp_config_converter.models import MCPConfig
from mcp_config_converter.parsers.base import BaseParser


class TOMLParser(BaseParser):
    """Parser for TOML configuration files."""

    def parse(self, content: str | bytes) -> MCPConfig:
        """Parse TOML content into MCPConfig model.

        Args:
            content: TOML content as string or bytes

        Returns:
            MCPConfig: Parsed configuration

        Raises:
            ImportError: If no TOML library is available
        """
        if isinstance(content, bytes):
            if tomllib is not None:
                data = tomllib.loads(content.decode("utf-8"))
            elif toml is not None:
                data = toml.loads(content.decode("utf-8"))
            else:
                raise ImportError("No TOML library available. Install with: pip install tomli")
        elif tomllib is not None:
            data = tomllib.loads(content)
        elif toml is not None:
            data = toml.loads(content)
        else:
            raise ImportError("No TOML library available. Install with: pip install tomli")

        return MCPConfig(**data)

    def parse_file(self, file_path: Path) -> MCPConfig:
        """Parse TOML file into MCPConfig model.

        Args:
            file_path: Path to TOML file

        Returns:
            MCPConfig: Parsed configuration
        """
        if tomllib is not None:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)
        elif toml is not None:
            with open(file_path) as f:
                data = toml.load(f)
        else:
            raise ImportError("No TOML library available. Install with: pip install tomli")

        return MCPConfig(**data)
