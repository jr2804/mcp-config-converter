"""Configuration transformation logic for MCP configs."""

from pathlib import Path
from typing import Dict, Optional, Union

from mcp_config_converter.models import MCPConfig
from mcp_config_converter.parsers import YAMLParser, JSONParser, TOMLParser
from mcp_config_converter.formatters import (
    ClaudeFormatter,
    GeminiFormatter,
    VSCodeFormatter,
    OpenCodeFormatter,
)


class ConfigTransformer:
    """Transform MCP configurations between formats and providers."""

    PARSERS = {
        'yaml': YAMLParser(),
        'yml': YAMLParser(),
        'json': JSONParser(),
        'toml': TOMLParser(),
    }

    FORMATTERS = {
        'claude': ClaudeFormatter(),
        'gemini': GeminiFormatter(),
        'vscode': VSCodeFormatter(),
        'opencode': OpenCodeFormatter(),
    }

    @classmethod
    def parse_file(cls, file_path: Union[str, Path]) -> MCPConfig:
        """Parse configuration file.

        Args:
            file_path: Path to configuration file

        Returns:
            MCPConfig: Parsed configuration

        Raises:
            ValueError: If file format is not supported
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lstrip('.')
        
        if suffix not in cls.PARSERS:
            raise ValueError(f"Unsupported file format: {suffix}. Supported: {list(cls.PARSERS.keys())}")
        
        parser = cls.PARSERS[suffix]
        return parser.parse_file(file_path)

    @classmethod
    def format_config(cls, config: MCPConfig, provider: str) -> str:
        """Format configuration for a specific provider.

        Args:
            config: MCPConfig to format
            provider: Target provider name

        Returns:
            Formatted configuration string

        Raises:
            ValueError: If provider is not supported
        """
        if provider not in cls.FORMATTERS:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported: {list(cls.FORMATTERS.keys())}"
            )
        
        formatter = cls.FORMATTERS[provider]
        return formatter.format(config)

    @classmethod
    def transform(
        cls,
        input_file: Union[str, Path],
        output_file: Optional[Union[str, Path]] = None,
        provider: Optional[str] = None,
    ) -> str:
        """Transform configuration from input file to target format/provider.

        Args:
            input_file: Input configuration file
            output_file: Output file path (optional)
            provider: Target provider (optional)

        Returns:
            Transformed configuration string
        """
        config = cls.parse_file(input_file)
        
        if provider:
            result = cls.format_config(config, provider)
        else:
            result = config.model_dump_json(indent=2)
        
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(result)
        
        return result
