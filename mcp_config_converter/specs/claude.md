# Claude MCP Configuration

Based on [Claude Code Docs](https://code.claude.com/docs/en/mcp).

## Configuration Scopes

### Project Scope

File: `.mcp.json` in project root.

### User Scope

File: `~/.claude.json`

## Configuration Structure

The configuration file uses a JSON structure with an `mcpServers` object.

```json
{
  "mcpServers": {
    "server-name": {
      "command": "executable",
      "args": ["arg1", "arg2"],
      "env": {
        "KEY": "value"
      }
    }
  }
}
```

### Server Definitions

#### Stdio Server (local)

```json
"my-server": {
  "command": "npx",
  "args": ["-y", "server-package"],
  "env": {
    "API_KEY": "secret"
  }
}
```

#### HTTP/SSE Server (remote)

```json
"remote-server": {
  "type": "http",  // or "sse"
  "url": "https://api.example.com/mcp",
  "headers": {
    "Authorization": "Bearer token"
  }
}
```

## Environment Variables

Supports expansion:

- `${VAR}`: Value of `VAR`
- `${VAR:-default}`: Value of `VAR` or `default` if unset
