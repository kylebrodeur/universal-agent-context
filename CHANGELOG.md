# Changelog

All notable changes to UACS (Universal Agent Context System) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-01-06

### 🎉 Initial Release

First public release of UACS - Universal Agent Context System for AI agent context management.

### ✨ Features

#### Core Functionality
- **Context Management**: Discover, translate, and manage AI agent context across multiple formats
- **Format Adapters**: Built-in support for `.cursorrules`, `.clinerules`, `.agents.md`, and agent skill formats
- **Context Compression**: Intelligent token reduction (70%+ compression ratio) while preserving semantic meaning
- **Marketplace Integration**: Search and install agent skills from multiple registries
- **Memory System**: Simple in-memory storage for agent context and history

#### MCP Server
- **Model Context Protocol Server**: Full MCP implementation exposing all UACS capabilities
- **Transport Modes**: Support for both stdio and SSE transports
- **Health Monitoring**: Built-in health check endpoint for Docker/production deployments

#### Distribution Methods
- **Python Package**: Install from GitHub with `uv pip install git+https://github.com/kylebrodeur/universal-agent-context.git`
- **Standalone Binary**: macOS ARM64 binary (23MB, <2s startup) - no Python required
- **Docker Image**: Optimized container (228MB) with uv package manager
- **CLI**: Full-featured command-line interface with 5 sub-commands

#### Documentation
- **Comprehensive Guides**: 9+ documentation files covering all features
- **Quick Start**: Step-by-step tutorials for common workflows
- **Examples**: 8 working code examples demonstrating library usage
- **API Reference**: Complete CLI and library API documentation

#### Quality & Testing
- **Test Coverage**: 145 unit tests + 18 integration tests (90%+ coverage)
- **Type Safety**: Full type hints with mypy checking
- **Code Quality**: Ruff linting, bandit security scanning
- **CI Ready**: Makefile with all quality checks

### 📦 Installation

#### Option 1: Python Package (via GitHub)
```bash
uv pip install git+https://github.com/kylebrodeur/universal-agent-context.git
```

#### Option 2: Standalone Binary (macOS ARM64)
```bash
# Download from GitHub Releases
# Or use the install script:
curl -fsSL https://raw.githubusercontent.com/kylebrodeur/universal-agent-context/main/scripts/install_mcp_server.sh | bash
```

#### Option 3: Docker
```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or docker run
docker run -d -p 3000:3000 --name uacs kylebrodeur/uacs:latest
```

### 🚀 Quick Start

```bash
# CLI: Discover available context formats
uacs skills discover

# CLI: Start MCP server
uacs serve --port 8080

# Python: Use the library
from uacs import UnifiedContext
context = UnifiedContext()
context.discover_adapters()
```

### 📊 Metrics

- **Binary Size**: 23MB (macOS ARM64)
- **Docker Image**: 228MB
- **Startup Time**: <2 seconds
- **Compression Ratio**: 70%+ typical
- **Test Coverage**: 90%+

### 🔧 Technical Details

- **Python Version**: 3.11+ required
- **Key Dependencies**: typer, rich, httpx, pydantic, tiktoken, mcp
- **Build System**: PyInstaller 6.17.0 for binaries
- **Package Manager**: uv (Astral) for fast installations
- **Container Base**: Alpine Linux with uv

### 📝 Documentation

- [README](README.md) - Project overview and quick start
- [Quick Start Guide](examples/README.md) - Step-by-step tutorials
- [Library Guide](docs/LIBRARY_GUIDE.md) - Python API documentation
- [CLI Reference](docs/CLI_REFERENCE.md) - Command-line usage
- [MCP Server Setup](docs/MCP_SERVER_SETUP.md) - MCP integration guide
- [Architecture](docs/ARCHITECTURE.md) - System design overview

### 🙏 Acknowledgments

This project builds on concepts from:
- Model Context Protocol (MCP) by Anthropic
- The AI agent skills ecosystem
- Multi-agent orchestration patterns

### 🔮 Coming Soon

- Windows and Linux binaries
- PyPI package distribution
- Claude Desktop integration guide
- Cursor and Windsurf integration guides
- Additional marketplace registries
- Enhanced memory system with semantic search

---

## Release Notes Template

For future releases, use this template:

## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements
