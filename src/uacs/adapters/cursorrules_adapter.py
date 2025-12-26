"""Adapter for Cursor .cursorrules format."""

from .base import BaseFormatAdapter, FormatAdapterRegistry, ParsedContent


@FormatAdapterRegistry.register
class CursorRulesAdapter(BaseFormatAdapter):
    """Cursor .cursorrules format adapter.

    Cursor rules are typically plain text instructions for the Cursor editor.
    """

    FORMAT_NAME = "cursorrules"
    SUPPORTED_FILES = [".cursorrules"]

    def parse(self, content: str) -> ParsedContent:
        """Parse .cursorrules format (usually plain text).

        Args:
            content: Raw .cursorrules content

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


__all__ = ["CursorRulesAdapter"]
