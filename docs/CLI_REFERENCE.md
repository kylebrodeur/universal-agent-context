# UACS CLI Reference

The `uacs` command-line interface provides tools for managing context, skills, marketplace packages, and memory.

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
- `read-properties`: Read specific properties from a skill. [[KB: Should be broken into read with --properties x or --properties x,y,z like we use flags for the other commands.]]

### `uacs marketplace`
Discover and install skills and MCP servers.

**Subcommands:**
- `search`: Search for packages.
  - `--type`: Package type (skills, mcp, all).
- `install`: Install a package.
  - `--type`: Package type.
- `list`: List installed packages.
- `uninstall`: Uninstall a package.

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
