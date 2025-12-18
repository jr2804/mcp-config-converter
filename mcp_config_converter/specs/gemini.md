# Gemini CLI MCP Configuration

Based on [Gemini CLI Docs](https://geminicli.com/docs/tools/mcp-server/).

## Configuration Files
- Project Scope: `.gemini/settings.json`
- User Scope: `~/.gemini/settings.json`

## Configuration Structure

The configuration file uses a JSON structure with `mcp` (global settings) and `mcpServers` (server definitions).

```json
{
  "mcp": {
    "serverCommand": "optional-global-command",
    "allowed": ["server1"],
    "excluded": ["server2"]
  },
  "mcpServers": {
    "server-name": {
      // Configuration properties
    }
  }
}
```

### Server Properties
- **Required (one of):**
  - `command`: Path to executable (stdio)
  - `url`: SSE endpoint URL
  - `httpUrl`: HTTP streaming endpoint URL

- **Optional:**
  - `args`: Array of arguments (stdio)
  - `cwd`: Working directory (stdio)
  - `env`: Environment variables object
  - `headers`: HTTP headers object (for url/httpUrl)
  - `timeout`: Timeout in ms (default 600000)
  - `trust`: Boolean, bypass confirmation (default false)
  - `includeTools`: List of tools to allow
  - `excludeTools`: List of tools to block

### Examples

#### Stdio Server

```json
"my-server": {
  "command": "python",
  "args": ["server.py"],
  "env": { "KEY": "val" },
  "trust": true
}
```

#### HTTP Server

```json
"http-server": {
  "httpUrl": "http://localhost:3000/mcp",
  "headers": {
    "Authorization": "Bearer token"
  }
}
```

#### SSE Server

```json
"sse-server": {
  "url": "http://localhost:8080/sse"
}
```
