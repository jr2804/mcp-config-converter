"""Formatter for OpenCode MCP configuration."""

from typing import Any

from mcp_config_converter.formatters.base import BaseFormatter
from mcp_config_converter.models import MCPConfig


class OpenCodeFormatter(BaseFormatter):
    """Formatter for OpenCode MCP configuration."""

    def format(self, config: MCPConfig) -> str:
        """Format MCPConfig into OpenCode configuration string (JSON).

        Args:
            config: MCPConfig to format

        Returns:
            Formatted configuration as JSON string
        """
        import json

        return json.dumps(self.format_dict(config), indent=2)

    def format_dict(self, config: MCPConfig) -> dict[str, Any]:
        """Format MCPConfig into OpenCode-specific dictionary structure.

        Args:
            config: MCPConfig to format

        Returns:
            Formatted configuration as dictionary
        """
        servers = {}
        for server_name, server in config.servers.items():
            servers[server_name] = {
                "display_name": server.name,
                "executable": server.command,
                "parameters": server.args or [],
                "environment_variables": server.env or {},
            }
            if server.metadata:
                servers[server_name]["metadata"] = server.metadata

        return {
            "format_version": config.version,
            "mcp_servers": servers,
        }
