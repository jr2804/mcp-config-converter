# LLxprt Code MCP Configuration

Based on [MCP servers with the LLxprt Code](https://github.com/vybestack/llxprt-code/blob/main/docs/tools/mcp-server.md).

## Configuration File

File: `settings.json` (likely `~/.llxprt/settings.json`).
Schema: `https://charm.land/crush.json`

## Configuration Structure

The configuration uses a JSON structure with an `mcp` object for definitions and `tools` object for enabling/disabling.

```json
{
  "$schema": "https://charm.land/crush.json",
  "mcp": {
    "my-server": {
      "type": "local",
      "command": ["executable", "arg1"],
      "enabled": true,
      "environment": {
        "KEY": "VALUE"
      }
    }
  },
  "tools": {
    "my-server*": true
  }
}
```

### Server Types

#### Local Server

```json
"local-server": {
  "type": "local",
  "command": ["npx", "-y", "server-package"],
  "enabled": true,
  "environment": { "VAR": "val" },
  "timeout": 60
}
```

#### Remote Server

```json
"remote-server": {
  "type": "remote",
  "url": "https://api.example.com",
  "enabled": true,
  "headers": {
    "Authorization": "Bearer token"
  },
  "oauth": { ... } // optional
}
```

### Tool Control

Manage tool availability globally or per-agent.

```json
"tools": {
  "server_prefix*": false // Disable globally
},
"agent": {
  "my-agent": {
    "tools": {
      "server_prefix*": true // Enable for this agent
    }
  }
}
```
