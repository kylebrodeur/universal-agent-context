# UACS Format Adapters

## Overview
The UACS Format Adapter system allows the Universal Agent Context System to understand and translate various agent configuration formats into a unified structure. This enables cross-tool compatibility, allowing you to use `.cursorrules`, `.clinerules`, `SKILLS.md`, and `AGENTS.md` interchangeably.

## Built-in Adapters

### AgentSkillAdapter
Supports the vendor-neutral [Agent Skills](https://agentskills.io) format.
- **Directories**: `.agent/skills/` (recommended), `.claude/skills/` (for importing external repos)
- **Precedence**: `.agent/` > `.claude/` (allows local overrides of external skills)
- **Files**: `SKILL.md` (required), `scripts/`, `references/`, `assets/` (optional)
- **Format spec**: https://agentskills.io/specification

**Validation expectations:**
The AgentSkillAdapter validates all SKILL.md files against the Agent Skills specification:
- ✅ YAML frontmatter with required fields: `name`, `description`
- ✅ Name must be kebab-case (lowercase, hyphens only), max 64 characters
- ✅ Description max 1024 characters, non-empty
- ✅ Only allowed frontmatter fields: `name`, `description`, `license`, `metadata`, `compatibility`, `allowed-tools`
- ✅ Directory name must match skill name
- ✅ Optional fields: `compatibility` (max 500 chars), `license`, `metadata`, `allowed-tools`

Invalid skills will generate warnings in `skills list` and errors during `packages install`.

**Precedence rules:**
When the same skill name exists in both directories, `.agent/` wins:
```
.agent/skills/pdf-processing/SKILL.md     ← Used (precedence)
.claude/skills/pdf-processing/SKILL.md    ← Ignored
```

This allows you to:
- Keep `.agent/` for custom/forked skills
- Use `.claude/` for imported third-party skills
- Override external skills with local modifications

### SkillsAdapter
Supports the legacy `SKILLS.md` format (multi-skill in single file).
- **File**: `SKILLS.md`
- **Status**: Legacy format, maintained for backward compatibility
- **Recommendation**: New projects should use AgentSkillAdapter with individual `SKILL.md` files

**Note:** This adapter does NOT follow the Agent Skills specification. It's a different format where multiple skills are defined in one `SKILLS.md` file with section-based parsing. For the official Agent Skills format, use `AgentSkillAdapter` instead.

### AgentsMDAdapter
Supports the `AGENTS.md` format for defining agent roles and global instructions.
- **File**: `AGENTS.md`

### CursorRulesAdapter
Supports the `.cursorrules` format used by the Cursor editor.
- **File**: `.cursorrules`

### ClineRulesAdapter
Supports the `.clinerules` format used by the Cline (formerly Claude Dev) VS Code extension.
- **File**: `.clinerules`
- **Use case**: Allows Cline users to reuse their existing rules with UACS
- **Format**: Plain text instructions, similar to system prompts

## ParsedContent Structure
Every adapter produces a `ParsedContent` object after parsing. This object contains:
- `instructions`: The core system instructions.
- `metadata`: Format-specific metadata (e.g., author, version).
- `triggers`: (Optional) Keywords or patterns that activate this content.

## Creating Custom Adapters
You can create custom adapters by inheriting from `BaseFormatAdapter`.

```python
from pathlib import Path
from uacs.adapters.base import BaseFormatAdapter, ParsedContent

class MyFormatAdapter(BaseFormatAdapter):
    FORMAT_NAME = "my_format"
    SUPPORTED_FILES = ["MY_CONFIG.md"]
    
    def parse(self, content: str) -> ParsedContent:
        # Implement your parsing logic here
        instructions = self._extract_instructions(content)
        return ParsedContent(instructions=instructions, metadata={"type": "custom"})
        
    def to_system_prompt(self) -> str:
        if not self.parsed:
            return ""
        return f"### CUSTOM INSTRUCTIONS\n{self.parsed.instructions}"
        
    def _extract_instructions(self, content: str) -> str:
        # Helper for parsing
        return content.strip()
```

## Adapter Registration
Adapters are automatically discovered by the `UnifiedContextAdapter` based on the files present in the workspace.

## Translation Patterns

### `to_system_prompt()`
Converts the parsed content into a string suitable for inclusion in an LLM's system prompt.

### `to_adk_capabilities()`
Converts the parsed content into a dictionary compatible with Google ADK's agent card format, allowing agents to "know" what they are capable of.

## Related Documentation

- [UACS Package Management](./PACKAGES.md) - Installing and validating skills
- [Context Management](./CONTEXT.md) - Using parsed content
- [Agent Skills Specification](https://agentskills.io/specification) - Official format
