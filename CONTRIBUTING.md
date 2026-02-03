# Contributing to UACS

Thank you for your interest in contributing to the Universal Agent Context System (UACS)! This document provides guidelines and instructions for contributing.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)
- [Questions & Support](#questions--support)

---

## Getting Started

### Prerequisites

- **Python 3.11+** (required for modern type hints)
- **uv** (recommended) or pip for package management
- **Git** for version control

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/universal-agent-context.git
   cd universal-agent-context
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/kylebrodeur/universal-agent-context.git
   ```

---

## Development Environment

### Quick Setup

```bash
# Install uv (recommended package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies
uv sync --all-extras

# Verify installation
make all  # Runs format + lint + type-check + security + test
```

> **📖 Detailed Setup Instructions**  
> For alternative installation methods, IDE configuration, and debugging tips, see the [Development Guide](docs/guides/DEVELOPMENT.md).

### Essential Commands

```bash
make all      # Run all checks before committing
make test     # Run test suite
make format   # Auto-format code
make lint     # Check code style
```

**See [Development Guide](docs/guides/DEVELOPMENT.md) for the complete list of commands and tool configurations.**

---

## Code Style

We use modern Python tooling for code quality:

- **Ruff** for formatting and linting (88 char line length)
- **MyPy** for static type checking
- **Python 3.11+** required

### Key Requirements

**1. Type hints on all functions:**
```python
def parse_skills(content: str) -> list[Skill]:
    """Parse skills from markdown content."""
    ...
```

**2. Google-style docstrings for public APIs:**
```python
def add_entry(self, content: str, agent: str) -> str:
    """Add a context entry.

    Args:
        content: The content to store
        agent: Name of the agent

    Returns:
        The unique entry ID
    """
```

**3. Use dataclasses for structured data:**
```python
@dataclass
class Skill:
    name: str
    instructions: str
    triggers: list[str]
```

**4. Use async/await for I/O operations**

> **📖 Complete Style Guide**  
> For detailed examples, import ordering, and modern Python best practices, see the [Development Guide](docs/guides/DEVELOPMENT.md).

---

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
uv run pytest tests/ --cov=src/uacs --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Writing Tests

Test files mirror source structure:
```
src/uacs/adapters/skills_adapter.py
→ tests/adapters/test_skills_adapter.py
```

**Basic test example:**
```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    """Create a sample file for testing."""
    file = tmp_path / "test.md"
    file.write_text("# Test Content")
    return file

def test_parse_file(sample_file: Path):
    """Test file parsing."""
    result = parse(sample_file)
    assert result is not None
```

### Requirements

- All new features must have tests
- Aim for 80%+ code coverage
- Test both success and error cases
- Use descriptive test names: `test_compression_reduces_tokens_by_70_percent`

> **📖 Advanced Testing**  
> For async tests, fixtures, and debugging techniques, see the [Development Guide](docs/guides/DEVELOPMENT.md).

---

## Pull Request Process

### Before Submitting

1. **Run all checks:**
   ```bash
   make all  # format + lint + type + security + test
   ```

2. **Verify tests pass:**
   ```bash
   uv run pytest tests/ -v
   ```

3. **Update documentation** if you changed APIs

4. **Add examples** if you added features

### PR Title Format

Use conventional commit style:

```
feat: Add support for .windsurf format
fix: Correct token counting in compression
docs: Update ARCHITECTURE.md with new diagrams
test: Add tests for package caching
refactor: Extract adapter registry to separate module
```

### PR Description Template

```markdown
## Description
Brief summary of changes.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for this change
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines (ruff, mypy)
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No new warnings
```

### Review Process

1. **Automated checks** run on every PR (GitHub Actions)
2. **Maintainer review** (usually within 48 hours)
3. **Address feedback** by pushing new commits
4. **Squash and merge** once approved

### After Merge

- Your contribution will be included in the next release
- You'll be added to the contributors list
- Thank you! 🎉

---

## Project Structure

Understanding the codebase layout:

```
universal-agent-context/
├── src/uacs/                    # Main source code
│   ├── __init__.py
│   ├── api.py                   # Public API (UACS class)
│   ├── adapters/                # Format translation
│   │   ├── base.py              # BaseFormatAdapter
│   │   ├── skills_adapter.py    # SKILLS.md
│   │   ├── agents_md_adapter.py # AGENTS.md
│   │   └── ...                  # Other formats
│   ├── context/                 # Context management
│   │   ├── unified_context.py   # UnifiedContextAdapter
│   │   ├── shared_context.py    # SharedContextManager
│   │   └── agent_context.py     # AgentContextBuilder
│   ├── packages/                 # Package discovery
│   │   ├── manager.py            # Package manager
│   │   ├── repositories.py       # Git repo management
│   │   ├── packages.py           # Package metadata
│   │   └── cache.py              # Caching layer
│   ├── memory/                  # Persistent storage
│   │   ├── simple_memory.py     # Key-value store
│   │   └── retrieval.py         # Semantic search
│   ├── protocols/mcp/           # MCP server
│   │   └── server.py            # stdio server
│   ├── cli/                     # CLI commands
│   │   ├── main.py              # Main app
│   │   ├── skills.py            # Skills commands
│   │   ├── packages_cli.py      # Package commands
│   │   └── ...
│   └── utils/                   # Shared utilities
│       ├── compression.py       # Compression helpers
│       └── token_counter.py     # Token counting
│
├── tests/                       # Test suite (mirrors src/)
│   ├── adapters/
│   ├── context/
│   ├── packages/
│   └── ...
│
├── examples/                    # Usage examples
│   ├── basic_context.py
│   ├── package_search.py
│   └── ...
│
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md
│   ├── LIBRARY_GUIDE.md
│   ├── CLI_REFERENCE.md
│   └── ...
│
├── pyproject.toml               # Project config + dependencies
├── Makefile                     # Development commands
└── README.md                    # Main documentation
```

### Key Files to Know

- **`src/uacs/api.py`** - Main entry point (`UACS` class)
- **`src/uacs/adapters/base.py`** - Extend this for new formats
- **`src/uacs/cli/main.py`** - CLI application
- **`pyproject.toml`** - Dependencies and metadata
- **`Makefile`** - Common development commands

---

## Questions & Support

### Where to Ask Questions

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and ideas
- **Documentation** - Check [docs/](docs/) first

### Reporting Bugs

Include:
1. UACS version: `uv run uacs --version`
2. Python version: `python --version`
3. Operating system
4. Minimal reproduction steps
5. Expected vs actual behavior
6. Error messages/logs

---

## Additional Resources

- [Development Guide](docs/guides/DEVELOPMENT.md) - Detailed tool configuration and IDE setup
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Library Guide](docs/LIBRARY_GUIDE.md)
- [CLI Reference](docs/CLI_REFERENCE.md)
- [Package Management Guide](docs/features/PACKAGES.md)

---

## License

By contributing to UACS, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to UACS!** 🚀

