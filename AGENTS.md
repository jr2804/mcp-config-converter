# Project Guidelines for Agentic Coding

This file serves as a central entry point for project-specific documentation located in `docs/agents-md/`.

## Universal Skills (Cross-Project)

The `.claude/skills` directory contains universal, reusable guidance that applies across all projects. Coding assistants should consult these skills for general best practices:

### Development Skills

- [coding_principles](docs/.claude/skills/development/coding_principles/SKILL.md) - Version control, code quality, comments
- [python_guidelines](docs/.claude/skills/development/python_guidelines/SKILL.md) - Python best practices, type hints, imports
- [python_cli](docs/.claude/skills/development/python_cli/SKILL.md) - CLI parameter handling, environment variables
- [testing_strategy](docs/.claude/skills/development/testing_strategy/SKILL.md) - Testing patterns, coverage, fixtures
- [uv_mcp](docs/.claude/skills/development/uv_mcp/SKILL.md) - UV package management workflows

### Tool Usage Skills

- [issue_tracking](docs/.claude/skills/tool_usage/issue_tracking/SKILL.md) - bd/beads workflow and commands
- [knowledge_management](docs/.claude/skills/tool_usage/knowledge_management/SKILL.md) - Memory storage and recall patterns
- [problem_solving](docs/.claude/skills/tool_usage/problem_solving/SKILL.md) - Sequential thinking and analysis
- [mcp_servers](docs/.claude/skills/tool_usage/mcp_servers/SKILL.md) - MCP server discovery and usage
- [serena](docs/.claude/skills/tool_usage/serena/SKILL.md) - Serena MCP server patterns
- [chunkhound](docs/.claude/skills/tool_usage/chunkhound/SKILL.md) - ChunkHound patterns

### Documentation Skills

- [documentation_standards](docs/.claude/skills/documentation/documentation_standards/SKILL.md) - Documentation best practices

## Project-Specific Documentation

The documentation files below contain **only project-specific** configurations, requirements, and conventions that are unique to this project:

- [000_General_Instructions.md](docs/agents-md/000_General_Instructions.md) - Project-specific requirements and conventions
- [100_Tool_Usage.md](docs/agents-md/100_Tool_Usage.md) - Tool configurations (SESSION CLOSE PROTOCOL, Memory Graph MCP setup)
- [600_Development.md](docs/agents-md/600_Development.md) - Project-specific development rules
- [700_Development_Testing.md](docs/agents-md/700_Development_Testing.md) - Project-specific testing configuration

**Note:** For universal coding practices, tool usage patterns, and development guidelines, always refer to the skills in `.claude/skills` first. The `docs/agents-md/` files contain only what is unique to this specific project.
