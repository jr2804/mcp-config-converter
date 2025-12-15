"""MCP configuration conversion prompt templates."""

import importlib.resources
import json
from typing import Any

from toon_format import decode, encode

from mcp_config_converter.prompts.base import BasePromptTemplate, PromptRegistry


@PromptRegistry.register("mcp_conversion")
class MCPConversionPrompt(BasePromptTemplate):
    """Prompt template for MCP configuration conversion using LLMs."""

    def __init__(self, target_provider: str, encode_toon: bool = True, decode_toon: bool = True, **kwargs: Any):
        """Initialize MCP conversion prompt.

        Args:
            target_provider: Target provider (claude, gemini, vscode, opencode)
            encode_toon: Whether to encode JSON input to TOON format
            decode_toon: Whether to decode TOON output back to JSON
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self.target_provider = target_provider.lower()
        self.encode_toon = encode_toon
        self.decode_toon = decode_toon

        # Output format depends on decode_toon setting
        self.output_format = "TOON" if self.decode_toon else "JSON"

    def _load_template(self, template_path: str) -> str:
        """Load a markdown template file with strict error handling."""
        try:
            files = importlib.resources.files("mcp_config_converter.prompts.templates")
            template_file = files / template_path
            if not template_file.exists():
                raise FileNotFoundError(f"Required template file not found: {template_path}")
            content = template_file.read_text(encoding="utf-8")
            if not content.strip():
                raise ValueError(f"Template file is empty: {template_path}")
            return content
        except Exception as e:
            raise RuntimeError(f"Failed to load template {template_path}: {e}")

    def build_prompt(self, input_config: str, **context: Any) -> str:
        """Build the complete conversion prompt."""
        # Handle input encoding based on encode_toon setting
        template = self._load_template("input/section.md")
        if self.encode_toon:
            try:
                input_config_json = json.loads(input_config)
                processed_input = encode(input_config_json)

            except (json.JSONDecodeError, ValueError):
                # If input is not JSON, pass as plain text
                processed_input = input_config

            input_section = template.format(input_config=processed_input)
        else:
            input_section = template.format(input_config=input_config)

        prompt_parts = [
            self._load_template("system/instruction.md"),
            input_section,
            self._get_provider_specifications(),
            self._load_template("output/format.md").format(target_provider=self.target_provider, output_format=self.output_format),
            self._load_template("conversion/rules.md"),
            self._load_template("examples/conversions.md"),
            self._load_template("validation/instructions.md").format(output_format=self.output_format),
            self._load_template("output/instructions.md").format(target_provider=self.target_provider.upper(), output_format=self.output_format),
        ]

        return "\n\n".join(prompt_parts)

    def _get_provider_specifications(self) -> str:
        """Get target provider specifications."""
        specs = {
            "claude": {
                "name": "Anthropic Claude",
                "structure": {
                    "version": "1.0",
                    "tools": {
                        "server_name": {
                            "name": "Server Name",
                            "command": "executable_path",
                            "args": ["arg1", "arg2"],
                            "env": {"VAR": "value"},
                            "metadata": {"key": "value"},
                        }
                    },
                },
            },
            "gemini": {
                "name": "Google Gemini",
                "structure": {
                    "schemaVersion": "1.0",
                    "models": {
                        "server_name": {
                            "name": "Server Name",
                            "type": "mcp",
                            "command": "executable_path",
                            "arguments": ["arg1", "arg2"],
                            "environment": {"VAR": "value"},
                            "metadata": {"key": "value"},
                        }
                    },
                },
            },
            "vscode": {
                "name": "Visual Studio Code",
                "structure": {"[mcp-servers]": {"server_name": {"command": "executable_path", "args": ["arg1", "arg2"], "env": {"VAR": "value"}}}},
            },
            "opencode": {
                "name": "OpenCode",
                "structure": {
                    "mcp": {
                        "servers": {"server_name": {"name": "Server Name", "command": "executable_path", "args": ["arg1", "arg2"], "env": {"VAR": "value"}}}
                    }
                },
            },
        }

        if self.target_provider not in specs:
            raise ValueError(f"Unsupported target provider: {self.target_provider}")

        spec = specs[self.target_provider]
        structure_json = json.dumps(spec["structure"], indent=2)

        return f"""TARGET PROVIDER: {spec["name"]}
REQUIRED OUTPUT STRUCTURE:
```json
{structure_json}
```"""

    def validate_output(self, output: str) -> bool:
        """Validate output based on format settings.

        Args:
            output: Raw LLM output string

        Returns:
            True if output is valid
        """
        if self.decode_toon:
            # Validate TOON output can be decoded to valid JSON
            try:
                decoded = decode(output)
                return isinstance(decoded, dict) and len(decoded) > 0
            except Exception:
                return False
        else:
            # Validate JSON output directly
            try:
                parsed = json.loads(output)
                return isinstance(parsed, dict) and len(parsed) > 0
            except Exception:
                return False

    def parse_output(self, output: str) -> str:
        """Parse output and return as formatted JSON string.

        Args:
            output: Raw LLM output string

        Returns:
            Formatted JSON string
        """
        if self.decode_toon:
            # Parse TOON output
            try:
                decoded = decode(output)
                return json.dumps(decoded, indent=2)

            except Exception as e:
                raise ValueError(f"Failed to parse TOON output: {e}")
        else:
            # Output is already JSON, just validate and format it
            try:
                parsed = json.loads(output)
                return json.dumps(parsed, indent=2)
            except Exception as e:
                raise ValueError(f"Failed to parse JSON output: {e}")
