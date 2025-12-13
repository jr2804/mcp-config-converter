"""Formatter for Anthropic Claude MCP configuration."""

from typing import Any, Dict

from mcp_config_converter.models import MCPConfig
from mcp_config_converter.formatters.base import BaseFormatter


class ClaudeFormatter(BaseFormatter):
    """Formatter for Anthropic Claude MCP configuration."""

    def format(self, config: MCPConfig) -> str:
        """Format MCPConfig into Claude configuration string (JSON).

        Args:
            config: MCPConfig to format

        Returns:
            Formatted configuration as JSON string
        """
        import json
        return json.dumps(self.format_dict(config), indent=2)

    def format_dict(self, config: MCPConfig) -> Dict[str, Any]:
        """Format MCPConfig into Claude-specific dictionary structure.

        Args:
            config: MCPConfig to format

        Returns:
            Formatted configuration as dictionary
        """
        tools = {}
        for server_name, server in config.servers.items():
            tools[server_name] = {
                "name": server.name,
                "command": server.command,
                "args": server.args or [],
                "env": server.env or {},
            }
            if server.metadata:
                tools[server_name]["metadata"] = server.metadata
        
        return {
            "version": config.version,
            "tools": tools,
        }
