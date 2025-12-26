# Development Tools Guide

This document outlines the modern Python development tools configured for this project.

## ✅ Completed Updates

### 1. Tool Configuration
- ✅ Added comprehensive **Ruff** configuration (formatting + linting)
- ✅ Added strict **MyPy** type checking configuration
- ✅ Added **Pyright** for additional type checking
- ✅ Added **Bandit** security scanning configuration
- ✅ Added **pytest** with coverage configuration
- ✅ Updated all version constraints to match installed versions

### 2. New Files Created
- ✅ `.pre-commit-config.yaml` - Pre-commit hooks
- ✅ `Makefile` - Common development commands
- ✅ `.editorconfig` - Editor consistency
- ✅ `.github/workflows/ci.yml` - GitHub Actions CI pipeline (if applicable)

### 3. Documentation Updates
- ✅ Development tools configured for UACS
- ✅ Added security scan command
- ✅ Added parallel test execution command

## 🛠️ Tool Stack

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

## 📦 Installation

### Install All Dependencies
```bash
uv sync --all-extras
```

### Install Pre-commit Hooks
```bash
pre-commit install
# Or using make:
make pre-commit-install
```

## 🚀 Common Commands

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

## 📊 CI/CD

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

## 🎯 Modern Python Best Practices

### 1. Type Hints Everywhere
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

## 🔒 Security Best Practices

1. **Never commit secrets** - Use `.env` files (add to `.gitignore`)
2. **Run bandit regularly** - `make security` or `bandit -r src/`
3. **Keep dependencies updated** - Use `uv sync` and Dependabot
4. **Validate user input** - Use Pydantic for data validation
5. **Sanitize file paths** - Use `Path.resolve()` and check traversal

## 📈 Coverage Goals

- **Target**: 80%+ code coverage
- **View reports**: Open `htmlcov/index.html` after running `make test-cov`
- **Exclude**: Test files, `__main__` blocks, type checking blocks

## 🐛 Debugging

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

## 📚 Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [pre-commit Documentation](https://pre-commit.com/)

## 🎉 Quick Start Checklist

- [ ] Run `uv sync --all-extras`
- [ ] Run `make pre-commit-install`
- [ ] Run `make all` to verify everything works
- [ ] Configure your IDE to use ruff and mypy
- [ ] Set up your `.env` file for local development (if applicable)
- [ ] Review project documentation for UACS-specific guidelines

## 💡 IDE Setup

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

## 🔄 Migration Notes

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
