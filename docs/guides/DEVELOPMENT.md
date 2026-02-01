# Development Tools Guide

This document provides detailed technical reference for developers working on UACS. 

> **🚀 New Contributors:** Start with [CONTRIBUTING.md](../../CONTRIBUTING.md) for a quick-start guide to making your first contribution.

## Table of Contents

- [Installation Options](#installation-options)
- [Tool Stack](#tool-stack)
- [Common Commands](#common-commands)
- [Configuration Details](#configuration-details)
- [IDE Setup](#ide-setup)
- [Debugging](#debugging)
- [Code Style Deep Dive](#code-style-deep-dive)
- [Testing Advanced Topics](#testing-advanced-topics)
- [CI/CD](#cicd)
- [Migration Notes](#migration-notes)
- [Additional Resources](#additional-resources)

---

## Installation Options

### Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies
uv sync --all-extras

# Verify installation
uv run pytest tests/ --tb=short
```

### Using pip (Alternative)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode
pip install -e ".[dev,test,mcp]"

# Verify installation
pytest tests/ --tb=short
```

### Project-Specific Setup

```bash
# Initialize UACS directories (for testing CLI)
uv run uacs context init
uv run uacs memory init

# Install filesystem MCP server (for MCP tests)
npx -y @modelcontextprotocol/server-filesystem .
```

---

## Tool Stack

### Code Quality
- **Ruff** (v0.14.10) - Fast Python linter & formatter (replaces: black, isort, flake8)
- **MyPy** (v1.19.1) - Static type checker
- **Pyright** (v1.1.390+) - Microsoft's type checker (optional, stricter checks)
- **Bandit** (v1.7.10+) - Security vulnerability scanner

### Testing
- **pytest** (v9.0.2) - Testing framework
- **pytest-asyncio** (v1.3.0) - Async test support
- **pytest-cov** (v7.0.0) - Coverage reporting
- **pytest-mock** (v3.15.1) - Mocking support
- **pytest-xdist** (v3.6.0+) - Parallel test execution

### Development Workflow
- **pre-commit** (v4.0.0+) - Git hooks for code quality
- **uv** - Fast Python package installer

---

## Common Commands

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Using Make (Recommended)
```bash
make help              # Show all available commands
make dev-install       # Install all dependencies
make format            # Format code with ruff
make lint              # Lint code
make type-check        # Run mypy + pyright
make security          # Run security checks
make test              # Run tests
make test-cov          # Run tests with coverage
make test-parallel     # Run tests in parallel
make all               # Run all checks (format, lint, type-check, security, test)
make clean             # Clean build artifacts
```

### Direct Commands
```bash
# Formatting
ruff format src/ tests/              # Format code
ruff check --fix src/ tests/         # Fix auto-fixable lint issues

# Linting
ruff check src/ tests/               # Check for issues

# Type Checking
mypy src/                            # Type check with mypy
pyright src/                         # Type check with pyright (stricter)

# Testing
pytest tests/                        # Run tests
pytest tests/ -v                     # Verbose output
pytest tests/ -n auto                # Parallel execution
pytest tests/ --cov                  # With coverage
pytest tests/ -k "test_name"         # Run specific test

# Security
bandit -r src/                       # Security scan

# Pre-commit
pre-commit run --all-files           # Run all hooks manually
```

## 🔧 Configuration Details

### Ruff Configuration
Located in [pyproject.toml](../pyproject.toml):
- Line length: 88 (Black-compatible)
- Target: Python 3.11+
- Enabled rules: pycodestyle, pyflakes, isort, pyupgrade, bugbear, comprehensions, bandit, pytest-style, and more
- Per-file ignores for tests and examples

### MyPy Configuration
Located in [pyproject.toml](../pyproject.toml):
- Strict mode enabled
- Type checking for all code except tests
- Special overrides for third-party packages

### pytest Configuration
Located in [pyproject.toml](../pyproject.toml):
- Async mode: auto
- Coverage: enabled by default
- Test markers: slow, integration, unit
- HTML + XML coverage reports

### Pre-commit Hooks
Located in [.pre-commit-config.yaml](../.pre-commit-config.yaml):
1. Standard checks (trailing whitespace, YAML/TOML/JSON validation)
2. Ruff formatting & linting
3. MyPy type checking
4. Bandit security scanning
5. Poetry/pyproject.toml validation

## CI/CD

### GitHub Actions
If using GitHub Actions, configure [.github/workflows/ci.yml](../.github/workflows/ci.yml):
- Runs on: Ubuntu, macOS, Windows
- Python versions: 3.11, 3.12, 3.13
- Jobs:
  - Lint & format check
  - Type checking
  - Security scanning
  - Tests with coverage
  - Codecov integration

---

## Code Style Deep Dive

### Import Order

Imports should be organized in three groups:

```python
# 1. Standard library
import json
from pathlib import Path
from typing import Any

# 2. Third-party packages
import httpx
from pydantic import BaseModel

# 3. Local imports
from uacs.adapters.base import BaseFormatAdapter
from uacs.utils import token_counter
```

### Complete Docstring Example

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

### Modern Python Patterns
```python
from typing import Optional
from collections.abc import Sequence

def process_items(items: Sequence[str], limit: Optional[int] = None) -> list[str]:
    """Process items with optional limit."""
    return list(items[:limit]) if limit else list(items)
```

### 2. Use Modern Syntax
```python
# ✅ Good (Python 3.11+)
def get_names(data: list[dict[str, str]]) -> list[str]:
    return [item["name"] for item in data]

# ❌ Old style
from typing import List, Dict
def get_names(data: List[Dict[str, str]]) -> List[str]:
    ...
```

### 3. Dataclasses for Data Structures
```python
from dataclasses import dataclass

@dataclass
class Config:
    host: str
    port: int
    timeout: float = 30.0
```

### 4. Async/Await for I/O
```python
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### 5. Use pathlib
```python
from pathlib import Path

# ✅ Good
config_file = Path("config") / "settings.yaml"

# ❌ Old style
import os
config_file = os.path.join("config", "settings.yaml")
```

---

## Testing Advanced Topics

### Async Test Examples

```python
import pytest

@pytest.mark.asyncio
async def test_fetch_package():
    """Test async package fetching."""
    result = await fetch_package("https://api.example.com/package")
    assert result["name"] == "test-package"
```

### Complex Fixture Example

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

### Running Specific Tests

```bash
# Run specific test file
uv run pytest tests/adapters/test_skills_adapter.py -v

# Run tests matching pattern
uv run pytest tests/ -k "test_compression" -v

# Run tests in parallel
uv run pytest tests/ -n auto
```

---

## Security Best Practices

1. **Never commit secrets** - Use `.env` files (add to `.gitignore`)
2. **Run bandit regularly** - `make security` or `bandit -r src/`
3. **Keep dependencies updated** - Use `uv sync` and Dependabot
4. **Validate user input** - Use Pydantic for data validation
5. **Sanitize file paths** - Use `Path.resolve()` and check traversal

---

## Coverage Goals

- **Target**: 80%+ code coverage
- **View reports**: Open `htmlcov/index.html` after running `make test-cov`
- **Exclude**: Test files, `__main__` blocks, type checking blocks

---

## Debugging

### Run Tests with Debug Output
```bash
pytest tests/ -vv --log-cli-level=DEBUG
```

### Run Single Test File
```bash
pytest tests/test_specific.py -v
```

### Run Tests with pdb
```bash
pytest tests/ --pdb  # Drop into debugger on failure
```

---

## CI/CD

### GitHub Actions
If using GitHub Actions, configure [.github/workflows/ci.yml](../.github/workflows/ci.yml):
- Runs on: Ubuntu, macOS, Windows
- Python versions: 3.11, 3.12, 3.13
- Jobs:
  - Lint & format check
  - Type checking
  - Security scanning
  - Tests with coverage
  - Codecov integration

---

## IDE Setup

### VS Code
1. Install extensions:
   - Python (ms-python.python)
   - Ruff (charliermarsh.ruff)
   - MyPy Type Checker (ms-python.mypy-type-checker)

2. Add to `.vscode/settings.json`:
```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },
  "mypy-type-checker.args": ["--strict"],
  "python.analysis.typeCheckingMode": "strict"
}
```

### PyCharm
1. Settings → Tools → Python Integrated Tools:
   - Default test runner: pytest
   - Type checker: MyPy

2. Settings → Tools → External Tools:
   - Add Ruff for formatting and linting

---

## Migration Notes

### From Black to Ruff
- Ruff is 10-100x faster than Black
- Uses same formatting style (line length: 88)
- No code changes needed
- Update: `black .` → `ruff format .`

### From Flake8/isort to Ruff
- Ruff replaces both tools
- All rules configured in pyproject.toml
- Remove: `.flake8`, `setup.cfg` configs
- Update: `flake8 .` → `ruff check .`
