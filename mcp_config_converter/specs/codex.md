# OpenAI Codex MCP Configuration

Based on [Codex MCP Docs](https://developers.openai.com/codex/mcp/).

## Configuration File

File: `~/.codex/config.toml`

## Configuration Structure

The configuration uses TOML format. Each server is defined under `[mcp_servers.<name>]`.

```toml
# Stdio Server
[mcp_servers.my-server]
command = "npx"
args = ["-y", "server-package"]
cwd = "/path/to/cwd"  # Optional
[mcp_servers.my-server.env]
API_KEY = "secret"

# HTTP Server
[mcp_servers.remote-server]
url = "https://api.example.com/mcp"
bearer_token_env_var = "MY_TOKEN_VAR" # Optional
[mcp_servers.remote-server.http_headers]
X-Custom-Header = "value"
```

### Server Properties

#### Stdio (local)

- `command` (Required): Executable
- `args` (Optional): Arguments list
- `env` (Optional): Environment variables map
- `env_vars` (Optional): List of allowed env vars to forward
- `cwd` (Optional): Working directory

#### HTTP (remote)

- `url` (Required): Endpoint URL
- `bearer_token_env_var` (Optional): Env var for Bearer token
- `http_headers` (Optional): Static headers
- `env_http_headers` (Optional): Headers from env vars

#### Common Options

- `startup_timeout_sec`: Default 10
- `tool_timeout_sec`: Default 60
- `enabled`: Boolean
- `enabled_tools`: List of allowed tools
- `disabled_tools`: List of blocked tools
