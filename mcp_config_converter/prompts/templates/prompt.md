# CONVERSION RULES

1. PRESERVE ALL SEMANTICS: Command paths, arguments, environment variables, and metadata must be preserved exactly
2. SERVER IDENTIFIERS: Use server names as keys in the output structure
3. ENVIRONMENT VARIABLES: Convert between different naming conventions if needed (e.g., env vs environment)
4. ARGUMENTS: Maintain argument order and format
5. METADATA: Preserve all metadata fields, even if not standard
6. VALIDATION: Ensure commands exist (when possible) and arguments are reasonable
7. ERROR HANDLING: If conversion is impossible, explain why and suggest alternatives

## COMMON CONVERSION PATTERNS

- JSON/YAML/TOML/TOON input → Extract server definitions from any structure
- Free text input → Parse natural language descriptions of MCP servers
- Mixed formats → Use best judgment to identify server components
- Invalid input → Provide clear error message with conversion suggestions

INPUT CONFIGURATION:

```
{input_config}
```

TARGET SPECIFICATION:
{provider_spec}

## OUTPUT INSTRUCTIONS

1. If conversion fails, output a JSON object with an "error" field explaining the issue
2. Convert the input configuration to {target_provider} format
3. Do NOT include explanations, comments, or additional text!
4. Output ONLY the converted configuration in {output_format} format, without any additional text, markdown markups, HTML markups, formatting, or code blocks - just plain text!
5. Ensure the output can be directly parsed as {output_format} and decoded to valid JSON
