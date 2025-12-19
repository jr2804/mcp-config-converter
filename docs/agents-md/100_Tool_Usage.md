# Tools and MCP servers used for agentic coding

A concise, lint-friendly guide for contributors and agents working on this repository.

## Remarks on Tool Usage

If the coding agent, tool or any MCP server needs to create temporary files, test data, test results, or debug code (in particular those named `temp_*.*`, `tmp_*.*`, etc.), they **must** be created in the `/temp` directory. If `/temp` does not exist, it should be created. Never put temporary files in the root directory or any other directory.

## Tool: Issue tracking with beads (bd)

See `./110_Tool_beads.md` for detailed usage instructions.

## Tool: Memory-Graph

If MCP server `memorygraph` is available, recall project context using Memory-Graph when starting a new task:

```python
recall_memories(query="mcp server config converter implementation")
```

Store and recall relevant project-specific context (like `AGENTS.md` requirements or ongoing tasks) across turns; remind yourself of persisted notes before suggesting new changes to avoid repeating work.

See `./120_Tool_memorygraph.md` for detailed setup and usage instructions.

## Tool: Sequential Thinking

If MCP server `sequential-thinking` is available, use it to analyze problems through a flexible thinking process that can adapt and evolve.

See `./130_Tool_sequential_thinking.md` for detailed setup and usage instructions.

## Other recommended Tools

### subAgents

If the subagent capability is enabled, please create specialized subagents for complex workflows (e.g., multi-step refactors or downloads), delegate tasks and coordinate results before responding; mention in your summary which subagent was used if it changed the outcome.

### Code examples and documentation

If MCP server `context7` is available, always use it when code, setup or configuration steps are generated, or for library/API documentation. This means you should automatically use the Context7 MCP tools to resolve library id and get library docs without you having to explicitly ask.

### Tool discovery

If MCP server `ncp` is available, use it to discover the most suitable tools and currently available MCP servers for your current task:

- This server can analyze the task description and will delegate to other MCP servers or appropriate tools from its available set.
- Use before starting significant work to find optimal tools
- Example: `"I need to analyze test failures"` → ncp may suggest test analysis tools

### Desktop Commander

If MCP server `desktop-commander` is available, use this tool for:

- File system operations (create, edit, read directories)
- Process management and terminal interaction
- Search operations (files, content)
- Useful for workspace exploration and file organization

### Fetching web content

If MCP server `fetch` is available, use it to fetch web content and extract relevant information from given URLs.

### Additional MCP server search and selection

If MCP server `mcpadvisor` is available, use it to explore additional MCP servers and their capabilities, which might be useful for your task.

If MCP server `mcp-compass` is also available, use it to cross-check MCP servers identified by the `mcpadvisor` server.
