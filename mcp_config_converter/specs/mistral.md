# Mistral Vibe MCP Configuration

Based on [Mistral Vibe Docs](https://docs.mistral.ai/mistral-vibe/introduction/configuration#mcp-server-configuration).

## Configuration Format
Format: TOML (Array of tables `[[mcp_servers]]`)

## Configuration Structure

```toml
[[mcp_servers]]
name = "server_alias"
transport = "stdio" # or "http", "streamable-http"
command = "executable"
args = ["arg1", "arg2"]
# ... other properties
```

### Server Properties
- `name` (Required): Short alias
- `transport` (Required): `stdio`, `http`, or `streamable-http`

#### Stdio Transport
- `command`: Executable path
- `args`: Arguments list

#### HTTP Transport
- `url`: Base URL
- `headers`: Map of headers
- `api_key_env`: Env var for API key
- `api_key_header`: Header name for key (e.g. "Authorization")
- `api_key_format`: Format string (e.g. "Bearer {token}")

### Tool Filtering
Control availability with `enabled_tools` and `disabled_tools`.

```toml
enabled_tools = ["glob*", "re:^regex.*$"]
disabled_tools = ["exclude_*"]
```

### Examples

```toml
[[mcp_servers]]
name = "fetch_server"
transport = "stdio"
command = "uvx"
args = ["mcp-server-fetch"]

[[mcp_servers]]
name = "remote_server"
transport = "http"
url = "http://localhost:8000"
headers = { "Authorization" = "Bearer token" }
```
