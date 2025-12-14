"""Formatter for VS Code MCP configuration."""

from typing import Any

from mcp_config_converter.formatters.base import BaseFormatter
from mcp_config_converter.models import MCPConfig


class VSCodeFormatter(BaseFormatter):
    """Formatter for VS Code MCP configuration."""

    def format(self, config: MCPConfig) -> str:
        """Format MCPConfig into VS Code configuration string (JSON).

        Args:
            config: MCPConfig to format

        Returns:
            Formatted configuration as JSON string
        """
        import json

        return json.dumps(self.format_dict(config), indent=2)

    def format_dict(self, config: MCPConfig) -> dict[str, Any]:
        """Format MCPConfig into VS Code-specific dictionary structure.

        Args:
            config: MCPConfig to format

        Returns:
            Formatted configuration as dictionary
        """
        mcp_servers = {}
        for server_name, server in config.servers.items():
            mcp_servers[server_name] = {
                "command": server.command,
                "args": server.args or [],
            }
            if server.env:
                mcp_servers[server_name]["env"] = server.env

        return {"[mcp-servers]": mcp_servers}
