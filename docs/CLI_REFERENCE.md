# UACS CLI Reference

The `uacs` command-line interface provides tools for managing context, skills, packages, and memory.

## Global Options

- `--help`: Show help message and exit.
- `--version`: Show version number and exit.

## Commands

### `uacs serve`
Start the UACS MCP server for tool integration.

**Options:**
- `--host, -h`: Server host (default: localhost)
- `--port, -p`: Server port (default: 8080)

### `uacs context`
Manage unified context (AGENTS.md + SKILLS.md + Shared Memory).

**Subcommands:**
- `init`: Initialize AGENTS.md and context directories.
- `stats`: Show token usage and compression statistics.
- `capabilities`: Show loaded capabilities (skills, agents.md).
- `visualize`: Start real-time context dashboard.
- `graph`: Show context dependency graph.
- `compress`: Manually trigger context compression.
- `clear`: Clear shared context history.
- `snapshot`: Create a named snapshot of current context.
- `export`: Export context configuration to JSON.
- `report`: Generate detailed compression report.

### `uacs skills`
Manage agent skills.

**Subcommands:**
- `init`: Initialize SKILLS.md or .agent/skills directory.
- `list`: List available skills.
- `show`: Show details for a specific skill.
- `validate`: Validate skill format against specification.
- `test`: Test skill triggers against a query.
- `export`: Export skills to JSON.
- `read-properties`: Read specific properties from a skill.

### `uacs packages`
Manage agent skills and MCP servers.

**Subcommands:**
- `install`: Install a package from GitHub, Git URL, or local path.
  - `SOURCE`: GitHub repo (owner/repo), Git URL, or local path.
  - `--type`: Package type (skill, mcp, auto-detect).
- `list`: List installed packages.
  - `--type`: Filter by type (skill, mcp, all).
  - `--verbose`: Show detailed metadata.
- `validate`: Validate package structure.
  - `NAME_OR_PATH`: Package name or path to validate.
  - `--format`: Output format (text, json).
- `remove`: Uninstall a package.
  - `NAME`: Package name to remove.
  - `--force`: Skip confirmation prompts.
- `update`: Update installed packages.
  - `NAME`: Specific package to update (optional).
  - `--check-only`: Check for updates without installing.

### `uacs memory`
Manage persistent memory storage.

**Subcommands:**
- `init`: Initialize memory storage.
  - `--scope`: Scope to initialize (project, global, both).
- `stats`: Show memory usage statistics.
- `query`: Query memory store.
- `clear`: Clear memory store.

### `uacs mcp`
Manage Model Context Protocol integration.

**Subcommands:**
- `install`: Install an MCP server.
- `list`: List configured MCP servers.
- `config`: View or edit MCP configuration.

---

## Command Examples

### Package Management

**Install from GitHub:**
```bash
# Install using owner/repo syntax
uacs packages install anthropic/skills-testing

# Install specific package type
uacs packages install anthropic/skills-testing --type skill
```

**Install from Git URL:**
```bash
# HTTPS URL
uacs packages install https://github.com/owner/repo.git

# SSH URL
uacs packages install git@github.com:owner/repo.git
```

**Install from local path:**
```bash
# Absolute path
uacs packages install /path/to/local/skill

# Relative path
uacs packages install ./local-skills/my-skill
```

**List packages:**
```bash
# List all packages
uacs packages list

# List only skills
uacs packages list --type skill

# List with detailed metadata
uacs packages list --verbose
```

**Validate packages:**
```bash
# Validate installed package
uacs packages validate code-review

# Validate before installing
uacs packages validate /path/to/skill

# Get JSON output
uacs packages validate code-review --format json
```

**Remove packages:**
```bash
# Remove with confirmation
uacs packages remove code-review

# Force remove without prompts
uacs packages remove code-review --force
```

**Update packages:**
```bash
# Update all packages
uacs packages update

# Update specific package
uacs packages update code-review

# Check for updates without installing
uacs packages update --check-only
```

### Context Management

**View statistics:**
```bash
uacs context stats
```

**Compress context:**
```bash
uacs context compress --max-tokens 4000
```

**Clear context:**
```bash
uacs context clear
```

### Skills Management

**List skills:**
```bash
uacs skills list
```

**Validate skill:**
```bash
uacs skills validate .agent/skills/code-review/
```

**Convert formats:**
```bash
# Convert SKILLS.md to .cursorrules
uacs skills convert --to cursorrules

# Convert .cursorrules to SKILLS.md
uacs skills convert --from cursorrules --to skills
```

### Memory Management

**Add memory:**
```bash
# Add project memory
uacs memory add "Use pytest-asyncio for async tests" --scope project

# Add global memory
uacs memory add "Prefer TypeScript" --scope global --tags preference,language
```

**Search memory:**
```bash
uacs memory search "testing patterns"
```

**View statistics:**
```bash
uacs memory stats
```
