# VS Code MCP Configuration

Based on [VS Code MCP Docs](https://code.visualstudio.com/docs/copilot/customization/mcp-servers).

## Configuration File

File: `mcp.json` (Workspace or User specific locations).

## Configuration Structure

The file contains two main sections: `servers` and `inputs`.

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "my-api-key",
      "description": "Enter API Key",
      "password": true
    }
  ],
  "servers": {
    "server-name": {
      "type": "stdio", // or "http", "sse"
      "command": "executable",
      "args": ["arg1"],
      "env": {
        "API_KEY": "${input:my-api-key}"
      }
    }
  }
}
```

### Server Types

#### Stdio Server

```json
"my-local-server": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "server-package"],
  "env": { "VAR": "val" },
  "envFile": "${workspaceFolder}/.env"
}
```

#### HTTP/SSE Server

```json
"my-remote-server": {
  "type": "http", // or "sse"
  "url": "https://api.example.com/mcp",
  "headers": {
    "Authorization": "Bearer token"
  }
}
```

### Input Variables

Used for sensitive data.

- `type`: `promptString`
- `id`: Variable ID
- `description`: User prompt
- `password`: Boolean (mask input)
