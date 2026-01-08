# Project-Specific Tool Configuration

> **Note:** For universal MCP server patterns, memory storage, and problem-solving workflows, refer to the skills in `.claude/skills/tool_usage/`:
>
> - [mcp_servers](../../.claude/skills/tool_usage/mcp_servers/SKILL.md) - MCP server discovery and usage
> - [knowledge_management](../../.claude/skills/tool_usage/knowledge_management/SKILL.md) - Memory storage and recall patterns
> - [problem_solving](../../.claude/skills/tool_usage/problem_solving/SKILL.md) - Sequential thinking and analysis
> - [issue_tracking](../../.claude/skills/tool_usage/issue_tracking/SKILL.md) - bd/beads workflow and commands

## Project-Specific Rules

### Temporary File Location

If the coding agent, tool, or any MCP server needs to create temporary files, test data, test results, or debug code (in particular those named `temp_*.*`, `tmp_*.*`, etc.), they **must** be created in the `/temp` directory. If `/temp` does not exist, it should be created. Never put temporary files in the root directory or any other directory.

### subAgents Delegation

If the subagent capability is enabled, create specialized subagents for complex workflows (e.g., multi-step refactors or downloads), delegate tasks and coordinate results before responding; mention in your summary which subagent was used if it changed the outcome.

### Context7 for Library Documentation

If MCP server `context7` is available, always use it when code, setup or configuration steps are generated, or for library/API documentation. This means you should automatically use the Context7 MCP tools to resolve library id and get library docs without you having to explicitly ask.

## bd/beads: SESSION CLOSE PROTOCOL

> **Note:** For complete bd/beads workflow, commands, and best practices, see [issue_tracking](../../.claude/skills/tool_usage/issue_tracking/SKILL.md)

### 🚨 CRITICAL WORKFLOW 🚨

**Before saying "done" or "complete"**, you MUST run this checklist:

```shell
[ ] 1. git status              (check what changed)
[ ] 2. git add <files>         (stage code changes)
[ ] 3. bd sync                 (commit beads changes)
[ ] 4. git commit -m "..."     (commit code)
[ ] 5. bd sync                 (commit any new beads changes)
[ ] 6. git push                (push to remote)
```

**NEVER skip this.** Work is not done until pushed.

This 6-step protocol is specific to this project's git workflow integration with beads.

## Memory Graph MCP Setup

> **Note:** For universal memory storage patterns, recall workflows, and best practices, see [knowledge_management](../../.claude/skills/tool_usage/knowledge_management/SKILL.md)

### Project Configuration

To enable the Memory Graph tool for this project, add the following to your `mcp.json` (project or user) configuration file:

```json
{
    "servers": {
        "memorygraph": {
            "command": "uvx",
            "type": "stdio",
            "args": [
                "--refresh",
                "--from",
                "https://github.com/gregorydickson/memory-graph.git",
                "--",
                "memorygraph",
                "--profile",
                "extended"
            ],
            "env": {
                "PYTHONIOENCODING": "utf-8"
            }
        }
    }
}
```

**Important:** The `PYTHONIOENCODING: utf-8` environment variable is required for proper Unicode handling in this project.

See [memory-graph](https://github.com/gregorydickson/memory-graph) for more details.

### Timing Mode

For this project, the default timing mode is `on-commit`:

`memory_mode: immediate | on-commit | session-end`

This can be adjusted based on workflow preferences.

