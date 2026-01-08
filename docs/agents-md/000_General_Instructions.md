# Project-Specific Instructions

> **Note:** For universal coding principles, version control practices, Python guidelines, and CLI patterns, refer to the skills in `.claude/skills/development/`:
>
> - [coding_principles](../../.claude/skills/development/coding_principles/SKILL.md) - Version control, comments, code quality
> - [python_guidelines](../../.claude/skills/development/python_guidelines/SKILL.md) - Python best practices, type hints
> - [python_cli](../../.claude/skills/development/python_cli/SKILL.md) - CLI parameter handling, environment variables

## Project-Specific Requirements

### Emoji Usage in Output

Use emojis in output if it enhances clarity and can be done consistently:

- ✔︎ for success
- ✘ for failure
- ∆ for user-facing warnings
- ‼︎ for user-facing errors

**DO NOT** use emojis gratuitously in comments or output. Use them ONLY when they have clear meanings (like success or failure).

### Environment Configuration

The repository contains a `.env.example` file in root, which contains example values and can be used as a template for creating temporary `.env` files during development/testing.

### Performance Considerations

- Optimize for performance using NumPy vectorized operations
- Avoid Python loops for signal processing tasks
- Profile and optimize critical code paths when necessary
- Ensure memory efficiency, especially for large audio files
- Benchmark against the reference implementation for speed comparison
- Consider using numba for performance-critical sections if needed

### LLM Implementation Notes

- Always prioritize legal compliance over code simplicity
- When in doubt about algorithmic choices, choose the more independent approach
- Focus on clear, readable code over micro-optimizations
- Test extensively against conformance data
- Document all major algorithmic decisions and their independence rationale
- Use modern Python idioms and best practices throughout

