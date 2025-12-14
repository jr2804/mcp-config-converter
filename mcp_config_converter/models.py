"""Pydantic models for MCP configuration."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MCPServer(BaseModel):
    """MCP Server configuration."""

    name: str = Field(..., description="Server name")
    command: str = Field(..., description="Command to start the server")
    args: list[str] | None = Field(default=None, description="Command arguments")
    env: dict[str, str] | None = Field(default=None, description="Environment variables")
    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata")


class MCPConfig(BaseModel):
    """Root MCP configuration model."""

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {"version": "1.0", "servers": {"example_server": {"name": "Example Server", "command": "python", "args": ["-m", "example_module"]}}}
        },
    )
    version: str = Field(default="1.0", description="Configuration version")
    servers: dict[str, MCPServer] = Field(default_factory=dict, description="MCP servers")
    metadata: dict[str, Any] | None = Field(default=None, description="Global metadata")
