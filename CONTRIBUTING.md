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

### Quick Setup (Recommended)

Using `uv` (fast and modern):

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies + dev tools
uv sync --all-extras

# Verify installation
uv run pytest tests/ --tb=short
```

### Alternative Setup (Using pip)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev,test,mcp]"

# Verify installation
pytest tests/ --tb=short
```

### Development Commands

```bash
# Format code (automatically fixes issues)
uv run ruff format src/ tests/

# Check linting
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/

# Type checking
uv run mypy src/

# Security scanning
uv run bandit -r src/

# Run all checks (format + lint + type-check + security + test)
make all

# Or individually
make format   # Format code
make lint     # Check linting
make test     # Run tests
make type     # Type check
make security # Security scan
```

### Project-Specific Setup

```bash
# Initialize UACS directories (optional, for testing CLI)
uv run uacs context init
uv run uacs memory init

# Install filesystem MCP server (for MCP tests)
npx -y @modelcontextprotocol/server-filesystem .
```

---

## Code Style

### Python Style Guide

We use **Ruff** for both formatting and linting:

- **Line length:** 88 characters (Black-compatible)
- **Python version:** 3.11+
- **Style guide:** PEP 8 + type hints

### Type Annotations

**All functions must have type annotations:**

```python
# ✅ Good
def parse_skills(content: str) -> List[Skill]:
    """Parse skills from markdown content."""
    pass

# ❌ Bad
def parse_skills(content):
    return []
```

### Docstrings

Use **Google-style docstrings** for all public APIs:

```python
def add_entry(
    self,
    content: str,
    agent: str,
    metadata: dict[str, Any] | None = None
) -> str:
    """Add a context entry to the shared context.

    Args:
        content: The content to store
        agent: Name of the agent creating the entry
        metadata: Optional metadata dictionary

    Returns:
        The unique entry ID

    Raises:
        ValueError: If content is empty

    Example:
        >>> ctx = SharedContextManager()
        >>> entry_id = ctx.add_entry("Hello", "claude")
    """
```

### Dataclasses Over Dicts

**Always use dataclasses for structured data:**

```python
# ✅ Good
from dataclasses import dataclass

@dataclass
class Skill:
    name: str
    instructions: str
    triggers: list[str]

# ❌ Bad
skill = {
    "name": "test",
    "instructions": "...",
    "triggers": []
}
```

### Async/Await

Use `async`/`await` for I/O operations:

```python
# ✅ Good
async def fetch_package(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ❌ Bad (blocking I/O)
import requests
def fetch_package(url: str) -> dict[str, Any]:
    return requests.get(url).json()
```

### Import Order

1. Standard library
2. Third-party packages
3. Local imports

```python
# Standard library
import json
from pathlib import Path
from typing import Any

# Third-party
import httpx
from pydantic import BaseModel

# Local
from uacs.adapters.base import BaseFormatAdapter
from uacs.utils import token_counter
```

---

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/adapters/test_skills_adapter.py -v

# Run with coverage
uv run pytest tests/ --cov=src/uacs --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Writing Tests

**Test structure mirrors source:**

```
src/uacs/adapters/skills_adapter.py
→ tests/adapters/test_skills_adapter.py

src/uacs/context/shared_context.py
→ tests/context/test_shared_context.py
```

**Use pytest fixtures for common setup:**

```python
import pytest
from pathlib import Path
from uacs.adapters.skills_adapter import SkillsAdapter

@pytest.fixture
def sample_skills_file(tmp_path: Path) -> Path:
    """Create a sample SKILLS.md file for testing."""
    skills_file = tmp_path / "SKILLS.md"
    skills_file.write_text("""
# Skills

## code-review
Reviews code for security and best practices.

**Triggers:** review, security, analyze
""")
    return skills_file

def test_skills_adapter_parse(sample_skills_file: Path):
    """Test that SkillsAdapter can parse skills."""
    adapter = SkillsAdapter(sample_skills_file)
    parsed = adapter.parse()
    
    assert len(parsed.skills) == 1
    assert parsed.skills[0].name == "code-review"
    assert "security" in parsed.skills[0].triggers
```

**Test async functions:**

```python
import pytest

@pytest.mark.asyncio
async def test_fetch_package():
    """Test async package fetching."""
    result = await fetch_package("https://api.example.com/package")
    assert result["name"] == "test-package"
```

### Test Requirements

- **All new features must have tests**
- **Aim for 80%+ code coverage**
- **Test both success and error cases**
- **Use descriptive test names**

```python
# ✅ Good test names
def test_compression_reduces_tokens_by_70_percent()
def test_marketplace_search_returns_empty_list_when_no_matches()
def test_adapter_raises_valueerror_on_invalid_format()

# ❌ Bad test names
def test_compression()
def test_search()
def test_adapter()
```

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
test: Add tests for marketplace caching
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
│   ├── marketplace/             # Package discovery
│   │   ├── marketplace.py       # Unified marketplace
│   │   ├── repositories.py      # Git repo management
│   │   ├── packages.py          # Package metadata
│   │   └── cache.py             # Caching layer
│   ├── memory/                  # Persistent storage
│   │   ├── simple_memory.py     # Key-value store
│   │   └── retrieval.py         # Semantic search
│   ├── protocols/mcp/           # MCP server
│   │   └── server.py            # stdio server
│   ├── cli/                     # CLI commands
│   │   ├── main.py              # Main app
│   │   ├── skills.py            # Skills commands
│   │   ├── marketplace_cli.py   # Marketplace commands
│   │   └── ...
│   └── utils/                   # Shared utilities
│       ├── compression.py       # Compression helpers
│       └── token_counter.py     # Token counting
│
├── tests/                       # Test suite (mirrors src/)
│   ├── adapters/
│   ├── context/
│   ├── marketplace/
│   └── ...
│
├── examples/                    # Usage examples
│   ├── basic_context.py
│   ├── marketplace_search.py
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

When reporting bugs, include:

1. **UACS version:** `uv run uacs --version`
2. **Python version:** `python --version`
3. **Operating system**
4. **Minimal reproduction steps**
5. **Expected vs actual behavior**
6. **Relevant error messages/logs**

### Suggesting Features

Before suggesting a feature:

1. Check if it already exists in the [roadmap](docs/IMPLEMENTATION_ROADMAP.md)
2. Search existing GitHub issues
3. Open a discussion to gather feedback
4. If approved, create an issue with detailed requirements

---

## Additional Resources

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Library Guide](docs/LIBRARY_GUIDE.md)
- [CLI Reference](docs/CLI_REFERENCE.md)
- [Marketplace Guide](docs/MARKETPLACE.md)
- [Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md)

---

## License

By contributing to UACS, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to UACS!** 🚀

