EXAMPLES:

Input (JSON):
{
  "mcpServers": {
    "my_server": {
      "command": "python",
      "args": ["-m", "my_module"],
      "env": {"DEBUG": "true"}
    }
  }
}

Output for Claude (JSON):
{
  "version": "1.0",
  "tools": {
    "my_server": {
      "name": "my_server",
      "command": "python",
      "args": ["-m", "my_module"],
      "env": {"DEBUG": "true"}
    }
  }
}

Input (YAML):
servers:
  - name: "file_server"
    command: "node"
    args: ["server.js", "--port", "3000"]
    environment:
      NODE_ENV: "production"

Output for VSCode (JSON):
{
  "[mcp-servers]": {
    "file_server": {
      "command": "node",
      "args": ["server.js", "--port", "3000"],
      "env": {"NODE_ENV": "production"}
    }
  }
}