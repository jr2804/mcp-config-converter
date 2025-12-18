# CONVERSION TASK

Your task is to convert MCP server configurations between different formats used by various coding agents and development environments. Output ONLY the converted configuration in `{output_format}` format, without any additional text, markdown markups, HTML markups, formatting, or code blocks.

## INPUT CONFIGURATION

This is the input configuration to be converted to `{output_format}` format:

```
{input_config}
```

## TARGET SPECIFICATION

{provider_spec}

## COMMON CONVERSION PATTERNS

- Determine input format (JSON, YAML, TOML, TOON, Free Text, Mixed, etc.) to be interpreted.
- For structured inputs, the root node name in the input needs to be identified (e.g., "mcp", "mcpServer", "servers", "mcp_servers", etc.).
- For free text input/Mixed formats, parse natural language descriptions of MCP servers. Use best judgment to identify server components and their parameters.
- Iterate over each server definition under the root node.
- Map server properties from input format to target format according to the target specification. Note that key names and value options may differ between server types (in particular local/stdio vs remote/http) based on properties.
- If the input is considered as invalid or incomplete, provide clear error message.
