# UACS Marketplace

## Overview
The UACS Marketplace provides unified access to skills and MCP servers from multiple sources. It allows developers to discover, install, and manage reusable capabilities for their AI agents.

**Key Features:**
- 🔍 Semantic search across multiple repositories
- 📦 One-command installation of skills and MCP servers
- ✅ Automatic validation on install (for Agent Skills)
- 🔄 Support for custom repository adapters
- 🏷️ Category and tag-based filtering

## Architecture
The marketplace system is built on a modular architecture:
- **MarketplaceAdapter**: The main entry point for searching and managing assets.
- **RepositoryAdapter**: Interface for different package sources (e.g., Smithery, SkillsMP).
- **Package Types**:
    - `SkillPackage`: Vendor-neutral agent skills (Agent Skills format).
    - `MCPPackage`: Model Context Protocol servers.

## Searching for Packages
You can search for packages using the `UACS` API or the CLI.

### Python API
```python
from pathlib import Path
from uacs import UACS

uacs = UACS(Path.cwd())
# Search for skills
results = uacs.search("python debugging", package_type="skills")

for package in results:
    print(f"Found: {package.name} - {package.description}")
```

### CLI
```bash
uacs marketplace search "python debugging" --type skills
```

## Supported Marketplaces
- **SkillsMP**: Aggregator for agent skills.
- **Smithery**: Registry for MCP servers.
- **Glama**: MCP server discovery.

## Installation Workflow
When a package is installed:
1. The `RepositoryAdapter` downloads the package content or configuration.
2. **Skills are validated** against the Agent Skills specification (see [Validation](#validation-on-install) below).
3. Skills are placed in the `.agent/skills/` directory.
4. MCP servers are registered in the local MCP configuration.
5. Local catalog is updated.

### Validation on Install

Skills installed via marketplace are automatically validated using the Agent Skills specification validator. This ensures packages meet quality standards before being added to your project.

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

## Adding Custom Repositories
You can extend the marketplace by implementing the `RepositoryAdapter` interface.

```python
from uacs.marketplace.repositories import RepositoryAdapter
from uacs.marketplace.packages import Package

class MyCustomRepo(RepositoryAdapter):
    async def search(self, query: str) -> List[Package]:
        # Implement search logic
        pass
        
    async def install(self, package: Package) -> Dict[str, Any]:
        # Implement installation logic
        pass
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
