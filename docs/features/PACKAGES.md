# UACS Package Management

## Overview
UACS provides a minimal package manager for installing and managing agent skills and MCP servers. It works like GitHub CLI extensions - install from GitHub, Git URLs, or local paths.

**Key Features:**
- 📦 Install packages from GitHub, Git URLs, or local paths
- ✅ Automatic validation on install (for Agent Skills)
- 📋 List installed packages with metadata
- 🔍 Validate package structure
- 🗑️ Clean uninstall with dependency tracking

## Installation Sources

### GitHub Repositories
Install directly from GitHub using `owner/repo` syntax:

```bash
# Install from GitHub
uacs packages install anthropic/skills-testing
uacs packages install owner/repo-name
```

### Git URLs
Install from any Git URL:

```bash
# Install from Git URL
uacs packages install https://github.com/owner/repo.git
uacs packages install git@github.com:owner/repo.git
```

### Local Paths
Install from local directories (useful for development):

```bash
# Install from local path
uacs packages install /path/to/local/skill
uacs packages install ./relative/path/to/skill
```

## Package Commands

### Install
Install a package from GitHub, Git URL, or local path:

```bash
# From GitHub
uacs packages install owner/repo

# From Git URL
uacs packages install https://github.com/owner/repo.git

# From local path
uacs packages install /path/to/package

# Specify package type (auto-detected by default)
uacs packages install owner/repo --type skill
uacs packages install owner/repo --type mcp
```

**Installation Process:**
1. Clone/copy package content
2. Validate package structure (for skills)
3. Place in appropriate directory (`.agent/skills/` or `.agent/mcpservers/`)
4. Update local catalog with metadata

### List
Show all installed packages:

```bash
# List all packages
uacs packages list

# Filter by type
uacs packages list --type skill
uacs packages list --type mcp

# Show detailed metadata
uacs packages list --verbose
```

**Output:**
```
📚 Installed Packages (5):

Skills:
  ✓ code-review               - Review code for security and best practices
    Source: github.com/anthropic/skills
    Installed: 2024-12-20

  ✓ documentation             - Generate comprehensive docs
    Source: github.com/anthropic/skills
    Installed: 2024-12-22

MCP Servers:
  ✓ filesystem                - File operations via MCP
    Source: github.com/anthropic/mcp-servers
    Installed: 2024-12-21
```

### Validate
Validate a package's structure and metadata:

```bash
# Validate installed package
uacs packages validate code-review

# Validate local package before install
uacs packages validate /path/to/package

# Get validation details in JSON
uacs packages validate code-review --format json
```

### Remove
Uninstall a package:

```bash
# Remove package
uacs packages remove code-review

# Force remove (skip confirmations)
uacs packages remove code-review --force
```

### Update
Update installed packages:

```bash
# Update all packages
uacs packages update

# Update specific package
uacs packages update code-review

# Check for updates without installing
uacs packages update --check-only
```

## Validation on Install

Skills installed via the package manager are automatically validated using the Agent Skills specification validator. This ensures packages meet quality standards before being added to your project.

**Validation checks:**
- ✅ YAML frontmatter structure is valid
- ✅ Required fields present: `name`, `description`
- ✅ Name follows kebab-case convention (lowercase, hyphens only)
- ✅ Field length constraints met (name: 64 chars, description: 1024 chars)
- ✅ Directory name matches skill name
- ✅ No unexpected frontmatter fields

If validation fails, the installation is aborted and structured errors are shown:

```
[ERROR] Skill validation failed for 'pdf-processing':
  • [name] Name contains uppercase letters. Must use lowercase only.
  • [directory] Directory name 'PDF_Processing' does not match skill name 'pdf-processing'

Package not installed. Please contact package author or report issue.
```

You can also manually validate skills:

```bash
# Validate a skill before or after install
uacs skills validate .agent/skills/pdf-processing/

# Get validation details in JSON
uacs skills read-properties .agent/skills/pdf-processing/ --format json
```

## Package Format Specifications

### SkillPackage
- **Format**: Agent Skills (https://agentskills.io)
- **Structure**:
    - `SKILL.md`: YAML frontmatter + Markdown instructions (required)
    - `scripts/`: Directory containing executable code (optional)
    - `references/`: Documentation and reference materials (optional)
    - `assets/`: Templates and resources (optional)
- **Frontmatter fields**:
    - `name` (required): kebab-case skill identifier, max 64 chars
    - `description` (required): Brief description, max 1024 chars
    - `license` (optional): License identifier (e.g., "Apache-2.0")
    - `metadata` (optional): Arbitrary key-value metadata
    - `compatibility` (optional): Environment requirements, max 500 chars
    - `allowed-tools` (optional): Space-delimited pre-approved tools

**Example SKILL.md:**
```markdown
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
compatibility: Requires Python 3.8+ and pdfplumber
---

# PDF Processing

## Instructions
Use this skill when working with PDF files...
```

See [Agent Skills Specification](https://agentskills.io/specification) for complete format details.

### MCPPackage
- **Format**: Model Context Protocol
- **Configuration**: Includes `install_command`, `env` variables, and `args`.

## Python API

You can also manage packages programmatically:

```python
from pathlib import Path
from uacs import UACS

uacs = UACS(Path.cwd())

# Install from GitHub
uacs.packages.install("anthropic/skills-testing")

# Install from local path
uacs.packages.install("/path/to/local/skill")

# List installed packages
packages = uacs.packages.list()
for package in packages:
    print(f"{package.name}: {package.description}")

# Validate package
validation = uacs.packages.validate("code-review")
if validation.is_valid:
    print("Package is valid!")
else:
    for error in validation.errors:
        print(f"Error: {error}")

# Remove package
uacs.packages.remove("code-review")
```

## Package Storage

**Skills:**
- Location: `.agent/skills/{skill-name}/`
- Metadata: `.agent/skills/.installed.json`

**MCP Servers:**
- Location: `.agent/mcpservers/{server-name}/`
- Metadata: `.agent/mcpservers/.installed.json`

**Metadata Format:**
```json
{
  "packages": {
    "code-review": {
      "name": "code-review",
      "type": "skill",
      "source": "github.com/anthropic/skills",
      "installed_at": "2024-12-20T10:30:00Z",
      "version": "1.0.0",
      "install_method": "github"
    }
  }
}
```

## Comparison with GitHub CLI Extensions

UACS package management is modeled after GitHub CLI extensions:

| Feature | GitHub CLI (`gh extension`) | UACS (`uacs packages`) |
|---------|----------------------------|------------------------|
| Install from GitHub | ✅ `gh extension install owner/repo` | ✅ `uacs packages install owner/repo` |
| Install from URL | ✅ `gh extension install https://...` | ✅ `uacs packages install https://...` |
| List installed | ✅ `gh extension list` | ✅ `uacs packages list` |
| Update packages | ✅ `gh extension upgrade` | ✅ `uacs packages update` |
| Remove packages | ✅ `gh extension remove` | ✅ `uacs packages remove` |
| Validation | ❌ None | ✅ Automatic validation |

**Philosophy:** Simple, Git-based package management without complex registries or search indices.
