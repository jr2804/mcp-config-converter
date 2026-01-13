"""Configuration transformation logic for MCP configs using LLMs."""

from pathlib import Path

from mcp_config_converter.llm import LiteLLMClient
from mcp_config_converter.prompts import build_conversion_prompt
from mcp_config_converter.types import PROVIDER_ALIAS_MAP
from mcp_config_converter.utils import clean_llm_output, convert_format


class ConfigTransformer:
    """Transform MCP configurations between formats and providers."""

    def __init__(self, llm_client: LiteLLMClient, encode_toon: bool = True):
        """Initialize the transformer with an LLM client.

        Args:
            llm_client: LiteLLM client instance for conversion
            encode_toon: Whether to encode structured input to TOON format for LLM
        """
        self.llm_client = llm_client
        self.encode_toon = encode_toon

    def transform(self, input_content: str, target_provider: str) -> str:
        """Transform configuration using LLM-based conversion.

        Args:
            input_content: Raw input configuration text
            target_provider: Target provider name

        Returns:
            Converted configuration string
        """
        if not target_provider:
            raise ValueError("Target provider is required for conversion")

        # Resolve provider aliases using the mapping
        actual_provider = PROVIDER_ALIAS_MAP.get(target_provider.lower(), target_provider)

        # Perform LLM-based conversion
        result = self._llm_convert(input_content, actual_provider)

        return result

    def transform_file(self, input_file: Path, target_provider: str) -> str:
        """Transform configuration from a file using LLM-based conversion.

        Args:
            input_file: Path to input configuration file
            target_provider: Target provider name

        Returns:
            Converted configuration string
        """
        # Read input content from file
        input_content = input_file.read_text(encoding="utf-8")

        # Resolve provider aliases using the mapping
        actual_provider = PROVIDER_ALIAS_MAP.get(target_provider.lower(), target_provider)

        # Perform transformation
        return self.transform(input_content, actual_provider)

    def _llm_convert(self, input_content: str, target_provider: str) -> str:
        """Perform LLM-based configuration conversion.

        Args:
            input_content: Raw input configuration text
            target_provider: Target provider name

        Returns:
            Converted configuration string
        """
        # Build prompt
        try:
            system_prompt, formatted_prompt = build_conversion_prompt(
                target_provider=target_provider,
                input_config=input_content,
                encode_toon=self.encode_toon,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create conversion prompt: {e}")

        # Generate conversion using LLM
        try:
            result = self.llm_client.generate(formatted_prompt, system_prompt=system_prompt)

            # Try to clean up the output (remove markdown code blocks, etc.)
            result = clean_llm_output(result)

            # validate and possibly correct output format
            result = convert_format(result, target_provider)
            """
            # Validate output
            if not validate_conversion_output(result):
                # Try to clean up the output (remove markdown code blocks, etc.)
                result = clean_llm_output(result)

                # Validate again
                if not validate_conversion_output(result):
                    raise ValueError("LLM output validation failed")
            """
            return result

        except Exception as e:
            raise RuntimeError(f"LLM conversion failed: {e}")
