# UACS Package Management

> **Note:** This document has been superseded by [PACKAGES.md](features/PACKAGES.md).
>
> The "marketplace" terminology has been replaced with "package management" for clarity.

## Quick Links

- **Package Management Guide**: [docs/features/PACKAGES.md](features/PACKAGES.md)
- **CLI Reference**: [docs/CLI_REFERENCE.md](CLI_REFERENCE.md)
- **Architecture**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)

## Overview

UACS includes a minimal package manager for discovering and installing:
- Agent skills
- MCP servers
- Configuration templates

For complete documentation, see [PACKAGES.md](features/PACKAGES.md).

## Quick Start

```bash
# Search for packages
uacs packages search <query>

# Install a package
uacs install <owner>/<repo>

# List installed packages
uacs packages list

# Uninstall a package
uacs uninstall <package-name>
```

For detailed usage, see the [Package Management Guide](features/PACKAGES.md).
