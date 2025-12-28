# SKILLS.md Format Documentation

**Date:** December 27, 2025  
**Purpose:** Document the legacy SKILLS.md format and its usage in UACS

---

## Overview

**SKILLS.md** is a **legacy format** for defining multiple agent skills in a single file. It was originally used by Anthropic's Claude tools and is maintained in UACS for backward compatibility.

⚠️ **Important:** This is **NOT** the same as the [Agent Skills specification](https://agentskills.io) which uses individual `SKILL.md` files.

---

## Format Specification

### File Structure

```markdown
# SKILLS.md

## Skill: Skill Name Here

**Description:** Brief description of what this skill does

**Triggers:** keyword1, keyword2, phrase with spaces

**Instructions:**
Detailed instructions for using this skill...
Can be multiple paragraphs.

---

## Skill: Another Skill

**Description:** Another skill description

**Triggers:** other, keywords

**Instructions:**
More instructions...
```

### Section Anatomy

Each skill has three required sections:

1. **Header** - `## Skill: {name}`
2. **Description** - `**Description:** {text}`
3. **Triggers** - `**Triggers:** {comma-separated}`
4. **Instructions** - `**Instructions:**` followed by content

---

## SKILLS.md vs SKILL.md (Agent Skills)

| Feature | SKILLS.md (Legacy) | SKILL.md (Agent Skills) |
|---------|-------------------|------------------------|
| **Format** | Multi-skill in one file | One skill per directory |
| **Standard** | Anthropic (informal) | agentskills.io spec |
| **Metadata** | Plain text sections | YAML frontmatter |
| **Location** | `~/.claude/SKILLS.md` | `.agent/skills/*/SKILL.md` |
| **Adapter** | `SkillsAdapter` | `AgentSkillAdapter` |
| **Status** | ✅ Legacy (maintained) | ✅ Recommended |
| **Validation** | Section parsing | YAML schema validation |
| **Trigger matching** | ✅ Implemented | ⚠️ Partial (see issues) |

### Example Comparison

**SKILLS.md (Legacy):**
```markdown
## Skill: Python Testing

**Description:** Run pytest with best practices

**Triggers:** test, pytest, testing

**Instructions:**
Run tests with: `pytest tests/ -v`
Use markers: `pytest -m unit`
```

**SKILL.md (Agent Skills):**
```markdown
---
name: python-testing
description: Run pytest with best practices
triggers:
  - test
  - pytest
  - testing
---

# Python Testing

Run tests with: `pytest tests/ -v`
Use markers: `pytest -m unit`
```

---

## Usage in UACS

### Adapter: SkillsAdapter

**Location:** `src/uacs/adapters/skills_adapter.py` (DOES NOT EXIST - adapter removed/refactored)

**Note:** The SkillsAdapter was mentioned in older documentation but does not exist as a separate file in the current codebase. The format translation functionality may have been:
1. Integrated into `AgentSkillAdapter`
2. Deprecated in favor of Agent Skills format
3. Or exists under a different name/location

### CLI Commands

```bash
# List skills from all sources (including SKILLS.md)
uacs skills list --all

# Convert from SKILLS.md to other formats
uacs skills convert --source SKILLS.md --target .cursorrules

# Test trigger matching (legacy SKILLS.md only)
uacs skills test "I need help with python testing"
```

### File Discovery

UACS looks for SKILLS.md in:
1. `~/.claude/SKILLS.md` (user-wide)
2. `./SKILLS.md` (project-specific)

### Token Counting

```bash
$ uacs context stats
Context Statistics:
  AGENTS.md:      460 tokens
  SKILLS.md:      0 tokens (none found)  ← Shows token count if found
  Shared Context: 0 tokens
```

---

## Code References in Codebase

### Mentions in Documentation

1. **[AGENTS.md](/Users/kylebrodeur/workspace/multi-agent-cli/AGENTS.md:15)**
   ```markdown
   - Context management (SKILLS.md + AGENTS.md + shared memory)
   ```

2. **[ADAPTERS.md](/Users/kylebrodeur/workspace/universal-agent-context/docs/ADAPTERS.md:39)**
   ```markdown
   ### SkillsAdapter
   Supports the legacy `SKILLS.md` format (multi-skill in single file).
   - **File**: `SKILLS.md`
   - **Status**: Legacy format, maintained for backward compatibility
   ```

3. **[ARCHITECTURE.md](/Users/kylebrodeur/workspace/universal-agent-context/docs/ARCHITECTURE.md:90)**
   ```markdown
   - `skills_adapter.py` - SKILLS.md format (Anthropic standard)
   ```

### CLI Implementation

**File:** `src/uacs/cli/context.py`

```python
# Line 38: Token counting display
console.print(f"  SKILLS.md:      {token_stats['skills_tokens']:>6,} tokens")

# Line 177-180: Loading SKILLS.md
# SKILLS.md
if skills_file and skills_file.exists():
    skills = SkillsAdapter(skills_file).parsed.skills
    console.print(f"\n[green]✓[/green] SKILLS.md loaded ({len(skills)} skills)")

# Line 200: Clear context (preserves SKILLS.md)
"""Clear all shared context (keeps SKILLS.md and AGENTS.md)."""

# Line 229: Validation
"""Validate AGENTS.md and SKILLS.md configuration."""
```

### MCP Server Integration

**File:** `src/uacs/protocols/mcp/skills_server.py`

```python
# Line 27: List skills tool
description="List all available skills from SKILLS.md",

# Lines 33, 50, 65: Optional path parameter
"description": "Optional path to SKILLS.md file",

# Line 73: Validation tool
description="Validate SKILLS.md file format",

# Line 190: Unified capabilities
description="Get all unified capabilities (SKILLS.md + AGENTS.md + Context)",
```

### MAOS Integration

**File:** `src/multi_agent_cli/cli/main.py`

```python
# Line 329: Chat command parameter
skills_path: Path | None = typer.Option(None, help="Path to SKILLS.md file"),

# Line 351: Usage example
$ multi-agent chat --skills-path ./SKILLS.md --agents-md-path .

# Line 381, 697: Function parameters
skills_path: Path to SKILLS.md
```

---

## Known Issues

### Issue 1: Trigger Matching Only Works with Legacy Format

**Source:** [COPILOT_INSTRUCTIONS_VALIDATION.md](/Users/kylebrodeur/workspace/multi-agent-cli/docs/executive-briefs/COPILOT_INSTRUCTIONS_VALIDATION.md:13)

```markdown
⚠️ **Issue Found:** Trigger matching only works with legacy SKILLS.md format

The `skills test` command only works with **SkillsAdapter** (legacy SKILLS.md format):

```python
# src/multi_agent_cli/cli/skills.py:202-227
@skills_app.command("test")
def test_skill(query: str, skills_file: Optional[Path] = None):
    adapter = SkillsAdapter(skills_file)  # ← Only uses SKILLS.md
    skill = adapter.find_skill_by_trigger(query)
```

**Impact:**
- ✅ Trigger matching works for SKILLS.md
- ❌ Trigger matching does NOT work for SKILL.md (Agent Skills)
```

### Issue 2: Adapter File Missing

**Discovery:** The `SkillsAdapter` is referenced throughout documentation and code, but the file `src/uacs/adapters/skills_adapter.py` does not exist.

**Possible reasons:**
1. Refactored into `AgentSkillAdapter`
2. Moved to a different location
3. Functionality merged with `base.py`

**Files that exist in `/src/uacs/adapters/`:**
- `__init__.py`
- `agent_skill_adapter.py` ✅
- `agents_md_adapter.py` ✅
- `base.py` ✅
- `clinerules_adapter.py` ✅
- `cursorrules_adapter.py` ✅

**Missing:**
- `skills_adapter.py` ❌ (referenced but doesn't exist)
- `gemini_adapter.py` ❌ (referenced in ARCHITECTURE.md but doesn't exist)

---

## Migration Path: SKILLS.md → SKILL.md

### Why Migrate?

1. **Standard Compliance** - Agent Skills is a formal specification
2. **Better Tooling** - Validation, IDE support, marketplace integration
3. **Modularity** - One skill per directory is easier to manage
4. **Community** - Growing ecosystem of Agent Skills packages

### Migration Steps

**Step 1: Split SKILLS.md into individual skills**

```bash
# From:
~/.claude/SKILLS.md
  ├─ Skill: Python Testing
  ├─ Skill: Code Review
  └─ Skill: Git Workflow

# To:
.agent/skills/
  ├─ python-testing/SKILL.md
  ├─ code-review/SKILL.md
  └─ git-workflow/SKILL.md
```

**Step 2: Convert format**

```bash
# Manual conversion or use CLI (if implemented)
uacs skills convert \
  --source ~/.claude/SKILLS.md \
  --target .agent/skills/ \
  --format agent-skills
```

**Step 3: Validate new skills**

```bash
uacs skills list --all
uacs skills validate .agent/skills/python-testing/
```

**Step 4: Update tooling references**

Remove references to `SKILLS.md` in:
- CLI commands
- Scripts
- Configuration files
- Documentation

**Step 5: Archive old SKILLS.md**

```bash
mv ~/.claude/SKILLS.md ~/.claude/SKILLS.md.backup
```

---

## Recommendations

### For Users

1. **New projects:** Use Agent Skills format (`.agent/skills/*/SKILL.md`)
2. **Existing SKILLS.md:** Continue using (fully supported)
3. **Migration:** Not urgent, but recommended for long-term

### For Developers

1. **Priority 1:** Document where `SkillsAdapter` actually lives
2. **Priority 2:** Fix trigger matching for Agent Skills format
3. **Priority 3:** Create migration tool (`skills migrate`)
4. **Priority 4:** Add deprecation warning to SKILLS.md commands

---

## Related Documentation

- [Agent Skills Specification](https://agentskills.io/specification) - Official SKILL.md standard
- [ADAPTERS.md](ADAPTERS.md) - Format adapter system overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - UACS system architecture
- [COPILOT_INSTRUCTIONS_VALIDATION.md](/Users/kylebrodeur/workspace/multi-agent-cli/docs/executive-briefs/COPILOT_INSTRUCTIONS_VALIDATION.md) - Trigger matching issues

---

## Appendix: Example SKILLS.md File

**Location:** `~/.claude/SKILLS.md`

```markdown
# SKILLS.md

My agent skills for development work.

---

## Skill: Python Testing

**Description:** Run pytest with best practices and coverage

**Triggers:** test, pytest, testing, coverage, unit test

**Instructions:**
Run tests with proper configuration:

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific markers
pytest -m unit  # Unit tests only
pytest -m integration  # Integration tests only

# Parallel execution
pytest tests/ -n auto
```

Best practices:
- Use fixtures for test setup
- Mock external dependencies
- Test edge cases
- Keep tests fast (< 1s each)

---

## Skill: Code Review

**Description:** Perform thorough code reviews with security focus

**Triggers:** review, code review, pr review, security review

**Instructions:**
Code review checklist:

1. **Functionality**
   - Does it solve the problem?
   - Are edge cases handled?
   - Is error handling comprehensive?

2. **Code Quality**
   - Is it readable?
   - Are names descriptive?
   - Is it DRY (Don't Repeat Yourself)?
   - Is complexity reasonable?

3. **Security**
   - Input validation
   - SQL injection risks
   - XSS vulnerabilities
   - Authentication/authorization

4. **Testing**
   - Are there tests?
   - Do tests cover edge cases?
   - Are mocks appropriate?

5. **Documentation**
   - Are docstrings present?
   - Is README updated?
   - Are breaking changes noted?

---

## Skill: Git Workflow

**Description:** Git best practices and common operations

**Triggers:** git, commit, branch, merge, rebase

**Instructions:**
Common Git workflows:

**Feature Branch Workflow:**
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Keep up to date with main
git fetch origin
git rebase origin/main

# Push to remote
git push origin feature/new-feature

# Create PR via GitHub CLI
gh pr create --title "Add new feature" --body "Description..."
```

**Commit Message Format:**
```
type(scope): subject

body (optional)

footer (optional)
```

Types: feat, fix, docs, style, refactor, test, chore

**Rebase vs Merge:**
- Use rebase for feature branches (clean history)
- Use merge for main/production (preserve context)
```

---

## File Locations in Codebase

### UACS Repository

**Documentation:**
- `/docs/ADAPTERS.md` - Adapter system (mentions SkillsAdapter)
- `/docs/ARCHITECTURE.md` - System design (mentions skills_adapter.py)
- `/docs/IMPLEMENTATION_ROADMAP.md` - Phase 1 tasks (deprecation warnings)

**Code (mentions but may not exist):**
- `/src/uacs/adapters/skills_adapter.py` - ❌ Does not exist
- `/src/uacs/cli/context.py` - Uses SKILLS.md (lines 38, 177-180, 200, 229)
- `/src/uacs/protocols/mcp/skills_server.py` - MCP tools (lines 27, 33, 50, 65, 73, 190, 247)

**Examples:**
- `/examples/` - May contain SKILLS.md usage examples (need to check)

### MAOS Repository

**Documentation:**
- `/AGENTS.md` - Project overview (line 15)
- `/.agent/skills/multi-agent-development/SKILL.md` - References test_skills_adapter.py (line 131)
- `/docs/ARCHITECTURE.md` - References SKILLS.md format (line 218)
- `/docs/executive-briefs/COPILOT_INSTRUCTIONS_VALIDATION.md` - Documents trigger matching issue (lines 13, 135)
- `/docs/IMPLEMENTATION_ROADMAP.md` - Deprecation notes (lines 1573, 1577)
- `/docs/PUBLIC_LAUNCH_PLAN.md` - What is SKILLS.md format (line 776)

**Code:**
- `/src/multi_agent_cli/cli/main.py` - CLI parameters (lines 329, 351, 381, 670, 697)
- `/src/multi_agent_cli/maos/plugins/skills_plugin.py` - Uses skills_adapters (lines 22-49)

**Tests:**
- `/tests/uacs/test_skills_adapter.py` - May exist (referenced in AGENTS.md line 73)

---

## Summary

**SKILLS.md** is a legacy format for defining agent skills in a single file. While still supported in UACS, the recommended approach is to use the [Agent Skills specification](https://agentskills.io) with individual `SKILL.md` files in `.agent/skills/` directories.

**Key Points:**
- ✅ **Supported:** SKILLS.md works and is maintained
- ⚠️ **Legacy:** Consider migrating to Agent Skills format
- ❌ **Adapter missing:** `skills_adapter.py` referenced but doesn't exist (needs investigation)
- 🐛 **Known issue:** Trigger matching only works with SKILLS.md, not SKILL.md
- 📚 **Documentation:** Extensive references throughout both UACS and MAOS codebases

**Next Steps:**
1. Locate or document where SkillsAdapter functionality actually exists
2. Fix trigger matching for Agent Skills format
3. Create migration tool for SKILLS.md → SKILL.md conversion
4. Add deprecation warnings (planned in Phase 1 of roadmap)
