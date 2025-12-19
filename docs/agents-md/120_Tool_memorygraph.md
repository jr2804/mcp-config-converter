# Memory Protocol

## Setup Instructions

To enable the Memory Graph tool in your agent, add the following to your
`mcp.json` (project or user) configuration file:

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

See [memory-graph](https://github.com/gregorydickson/memory-graph) for more details.

### REQUIRED: Before Starting Work

You MUST use `recall_memories` before any task. Query by project, tech, or task type.

### REQUIRED: Automatic Storage Triggers

Store memories on ANY of:

- **Git commit** → what was fixed/added
- **Bug fix** → problem + solution
- **Version release** → summarize changes
- **Architecture decision** → choice + rationale
- **Pattern discovered** → reusable approach

### Timing Mode (default: on-commit)

`memory_mode: immediate | on-commit | session-end`

### Memory Fields

- **Type**: solution | problem | code_pattern | fix | error | workflow
- **Title**: Specific, searchable (not generic)
- **Content**: Accomplishment, decisions, patterns
- **Tags**: project, tech, category (REQUIRED)
- **Importance**: 0.8+ critical, 0.5-0.7 standard, 0.3-0.4 minor
- **Relationships**: Link related memories when they exist

Do NOT wait to be asked. Memory storage is automatic.

## Summary

- **Always recall** before starting work to understand context
- **Always store** after implementing solutions, discovering patterns, or making architecture decisions
- **Link memories** with relationships to build knowledge graph
- **Use specific titles** that are searchable and descriptive
- **Tag consistently** with project and domain tags
- **Import from** `mcp_memorygraph_tools` for direct function access
