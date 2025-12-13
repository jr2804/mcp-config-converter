"""Formatter for Google Gemini MCP configuration."""

from typing import Any, Dict

from mcp_config_converter.models import MCPConfig
from mcp_config_converter.formatters.base import BaseFormatter


class GeminiFormatter(BaseFormatter):
    """Formatter for Google Gemini MCP configuration."""

    def format(self, config: MCPConfig) -> str:
        """Format MCPConfig into Gemini configuration string (JSON).

        Args:
            config: MCPConfig to format

        Returns:
            Formatted configuration as JSON string
        """
        import json
        return json.dumps(self.format_dict(config), indent=2)

    def format_dict(self, config: MCPConfig) -> Dict[str, Any]:
        """Format MCPConfig into Gemini-specific dictionary structure.

        Args:
            config: MCPConfig to format

        Returns:
            Formatted configuration as dictionary
        """
        models = {}
        for server_name, server in config.servers.items():
            models[server_name] = {
                "name": server.name,
                "type": "mcp",
                "command": server.command,
                "arguments": server.args or [],
                "environment": server.env or {},
            }
            if server.metadata:
                models[server_name]["metadata"] = server.metadata
        
        return {
            "schemaVersion": config.version,
            "models": models,
        }
