"""Pydantic models for MCP configuration."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MCPServer(BaseModel):
    """MCP Server configuration."""
    name: str = Field(..., description="Server name")
    command: str = Field(..., description="Command to start the server")
    args: Optional[List[str]] = Field(default=None, description="Command arguments")
    env: Optional[Dict[str, str]] = Field(default=None, description="Environment variables")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class MCPConfig(BaseModel):
    """Root MCP configuration model."""
    version: str = Field(default="1.0", description="Configuration version")
    servers: Dict[str, MCPServer] = Field(default_factory=dict, description="MCP servers")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Global metadata")

    class Config:
        """Pydantic config."""
        extra = "allow"
        json_schema_extra = {
            "example": {
                "version": "1.0",
                "servers": {
                    "example_server": {
                        "name": "Example Server",
                        "command": "python",
                        "args": ["-m", "example_module"]
                    }
                }
            }
        }
