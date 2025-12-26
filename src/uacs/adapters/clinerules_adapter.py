"""Adapter for Cline .clinerules format."""

from .base import BaseFormatAdapter, FormatAdapterRegistry, ParsedContent


@FormatAdapterRegistry.register
class ClineRulesAdapter(BaseFormatAdapter):
    """Cline .clinerules format adapter.

    Cline rules are typically plain text instructions for the Cline AI assistant.
    """

    FORMAT_NAME = "clinerules"
    SUPPORTED_FILES = [".clinerules"]

    def parse(self, content: str) -> ParsedContent:
        """Parse .clinerules format.

        Args:
            content: Raw .clinerules content

        Returns:
            ParsedContent with rules
        """
        return ParsedContent(rules=content.strip())

    def to_system_prompt(self) -> str:
        """Convert to system prompt.

        Returns:
            Formatted system prompt
        """
        if not self.parsed or not self.parsed.rules:
            return ""

        return f"# PROJECT RULES\n\n{self.parsed.rules}"


__all__ = ["ClineRulesAdapter"]
