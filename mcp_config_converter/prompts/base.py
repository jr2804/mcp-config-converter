"""Base classes for LLM prompt templates."""

from abc import ABC, abstractmethod
from typing import Any


class BasePromptTemplate(ABC):
    """Base class for LLM prompt templates."""

    def __init__(self, **kwargs: Any):
        """Initialize prompt template with configuration."""
        self.kwargs = kwargs

    @abstractmethod
    def build_prompt(self, input_config: str, **context: Any) -> str:
        """Build the complete prompt string.

        Args:
            input_config: The input configuration text to process
            **context: Additional context variables for prompt building

        Returns:
            Complete prompt string
        """
        pass

    def validate_output(self, output: str) -> bool:
        """Validate the LLM output.

        Args:
            output: Raw LLM output string

        Returns:
            True if output is valid
        """
        return True  # Default implementation - override in subclasses


class PromptRegistry:
    """Registry for prompt templates."""

    _registry: dict[str, type[BasePromptTemplate]] = {}

    @classmethod
    def register(cls, name: str) -> Any:
        """Decorator to register prompt templates."""

        def decorator(prompt_class: type[BasePromptTemplate]):
            cls._registry[name] = prompt_class
            return prompt_class

        return decorator

    @classmethod
    def get_template(cls, name: str) -> type[BasePromptTemplate]:
        """Get prompt template class by name."""
        return cls._registry[name]

    @classmethod
    def list_templates(cls) -> list[str]:
        """List all registered prompt templates."""
        return list(cls._registry.keys())
