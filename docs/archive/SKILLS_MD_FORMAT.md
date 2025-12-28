# SKILLS.md Format Documentation

**Date:** December 27, 2025  
**Purpose:** Document the DEPRECATED SKILLS.md format - NOT SUPPORTED in UACS

---

## Overview

**SKILLS.md** is a **DEPRECATED and UNSUPPORTED format** that was previously used for defining multiple agent skills in a single file. It was originally used by Anthropic's Claude tools.

🚫 **IMPORTANT: This format is NO LONGER SUPPORTED in UACS. Do not use it.**

✅ **Use Instead:** The [Agent Skills specification](https://agentskills.io) with individual `SKILL.md` files in `.agent/skills/` directories.

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
| **Adapter** | `SkillsAdapter` (removed) | `AgentSkillAdapter` |
| **Status** | 🚫 DEPRECATED (not supported) | ✅ Required |
| **Validation** | ❌ Not available | YAML schema validation |
| **Trigger matching** | ❌ Not available | ✅ Implemented |

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

### 🚫 NOT SUPPORTED

**Status:** SKILLS.md format is **NOT SUPPORTED** in UACS.

**What Happened:** 
- The `SkillsAdapter` has been completely removed
- All SKILLS.md file search paths have been removed
- CLI commands no longer recognize SKILLS.md format
- Token counting does not include SKILLS.md

### ✅ Use Agent Skills Instead

```bash
# List agent skills
uacs skills list --all

# Validate agent skills
uacs skills validate .agent/skills/

# Use agent skills directories only
.agent/skills/
  ├─ python-testing/SKILL.md
  ├─ code-review/SKILL.md
  └─ git-workflow/SKILL.md
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

1. **New projects:** ✅ MUST use Agent Skills format (`.agent/skills/*/SKILL.md`)
2. **Existing SKILLS.md:** 🚫 NO LONGER SUPPORTED - must migrate to Agent Skills
3. **Migration:** ⚠️ REQUIRED - SKILLS.md will not work

### For Developers

1. **Status:** SKILLS.md support has been completely removed
2. **Format:** Only Agent Skills specification is supported
3. **Migration:** Users must convert to `.agent/skills/` structure
4. **No Backward Compatibility:** SKILLS.md files will be ignored

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

**SKILLS.md** is a **DEPRECATED and UNSUPPORTED** format. It is **NOT SUPPORTED** in UACS.

**Key Points:**
- 🚫 **NOT SUPPORTED:** SKILLS.md does not work in UACS
- ✅ **Required Format:** Agent Skills specification (`.agent/skills/*/SKILL.md`)
- ❌ **Adapter Removed:** `skills_adapter.py` and SkillsAdapter have been removed
- ❌ **No File Discovery:** SKILLS.md paths removed from codebase
- 📚 **Migration Required:** All users must convert to Agent Skills format

**Action Required:**
1. ⚠️ **Remove any SKILLS.md files** from your projects
2. ✅ **Create `.agent/skills/` directory structure**
3. ✅ **Convert each skill** to individual SKILL.md files with YAML frontmatter
4. ✅ **Validate** using `uacs skills validate .agent/skills/`

**This format will not "sneak back in" - all backward compatibility has been removed.**
