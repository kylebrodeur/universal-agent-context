# UACS Build Scripts

This directory contains scripts for building and maintaining the UACS project.

## `build_mcp_server.py`

Builds the standalone MCP server binary using PyInstaller.

**Usage:**
```bash
python scripts/build_mcp_server.py [--platform {macos-arm64,macos-x86_64,linux-x86_64,windows-x86_64}]
```

**Artifacts:**
- Binaries are output to `dist/`
- Build artifacts are in `build/` (can be deleted)

## Other Scripts

- `install_mcp_server.sh`: (Planned) Installation script for Unix systems.
- `docker_quickstart.sh`: (Planned) Helper for Docker setup.
