"""Configuration transformation logic for MCP configs using LLMs."""

from pathlib import Path

from mcp_config_converter.llm import ProviderRegistry
from mcp_config_converter.prompts import PromptRegistry


class ConfigTransformer:
    """Transform MCP configurations between formats and providers."""

    @classmethod
    def transform(
        cls,
        input_file: str | Path | None = None,
        output_file: str | Path | None = None,
        provider: str | None = None,
        input_content: str | None = None,
        llm_provider: str | None = None,
        encode_toon: bool = True,
        decode_toon: bool = True,
    ) -> str:
        """Transform configuration using LLM-based conversion.

        Args:
            input_file: Input configuration file path (optional if input_content provided)
            output_file: Output file path (optional)
            provider: Target provider (required)
            input_content: Raw input configuration text (optional if input_file provided)
            llm_provider: Specific LLM provider to use for conversion (optional)
            encode_toon: Whether to encode JSON input to TOON format for LLM
            decode_toon: Whether to decode TOON output from LLM back to JSON
        """
        if not provider:
            raise ValueError("Target provider is required for conversion")

        # Get input content
        if input_file is not None:
            input_path = Path(input_file)
            input_content = input_path.read_text(encoding="utf-8")
        elif input_content is None:
            raise ValueError("Either input_file or input_content must be provided")

        # Perform LLM-based conversion
        result = cls._llm_convert(input_content, provider, llm_provider or "auto", encode_toon, decode_toon)

        # Write to output file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(result, encoding="utf-8")

        return result

    @classmethod
    def _llm_convert(
        cls,
        input_content: str,
        target_provider: str,
        llm_provider_name: str,
        encode_toon: bool,
        decode_toon: bool,
    ) -> str:
        """Perform LLM-based configuration conversion.

        Args:
            input_content: Raw input configuration text
            target_provider: Target provider name
            llm_provider_name: LLM provider to use for conversion
            output_format: Output format (json, yaml, etc.)

        Returns:
            Converted configuration string
        """
        # Get LLM provider
        try:
            # Create LLM provider instance directly (no configuration needed for conversion)
            llm_provider = ProviderRegistry.create_provider(llm_provider_name)

        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM provider {llm_provider_name}: {e}")

        # Get conversion prompt template
        try:
            prompt_template_class = PromptRegistry.get_template("mcp_conversion")
            prompt_template = prompt_template_class(target_provider=target_provider, encode_toon=encode_toon, decode_toon=decode_toon)
        except Exception as e:
            raise RuntimeError(f"Failed to create conversion prompt: {e}")

        # Build prompt
        prompt = prompt_template.build_prompt(input_config=input_content)

        # Generate conversion using LLM
        try:
            result = llm_provider.generate(prompt)

            # Validate output
            if not prompt_template.validate_output(result):
                # Try to clean up the output (remove markdown code blocks, etc.)
                result = cls._clean_llm_output(result)

                # Validate again
                if not prompt_template.validate_output(result):
                    raise ValueError("LLM output validation failed")

            return result

        except Exception as e:
            raise RuntimeError(f"LLM conversion failed: {e}")

    @classmethod
    def _clean_llm_output(cls, output: str) -> str:
        """Clean LLM output by removing markdown code blocks and extra text.

        Args:
            output: Raw LLM output

        Returns:
            Cleaned output
        """
        # Remove markdown code blocks
        if "```json" in output:
            # Extract JSON from code block
            start = output.find("```json") + 7
            end = output.find("```", start)
            if end > start:
                return output[start:end].strip()

        if "```yaml" in output:
            # Extract YAML from code block
            start = output.find("```yaml") + 7
            end = output.find("```", start)
            if end > start:
                return output[start:end].strip()

        if "```" in output:
            # Generic code block extraction
            start = output.find("```") + 3
            end = output.find("```", start)
            if end > start:
                return output[start:end].strip()

        # Return as-is if no code blocks found
        return output.strip()
