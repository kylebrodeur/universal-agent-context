# Agent Context for UACS Project

**Project:** Universal Agent Context System (UACS)
**Language:** Python 3.11+
**Package Manager:** uv

---

## Critical Commands

### Always Use `uv run` Prefix

**IMPORTANT:** This project uses `uv` for dependency management. Always prefix Python commands with `uv run`:

```bash
# ✅ CORRECT
uv run python script.py
uv run pytest tests/
uv run mypy src/

# ❌ WRONG
python script.py
pytest tests/
mypy src/
```

**Why:** Ensures we use the project's virtual environment (.venv) with correct dependencies.

---

## Project Structure

```
universal-agent-context/
├── src/uacs/               # Main package
│   ├── adapters/          # Format adapters (SKILLS.md, .cursorrules, etc.)
│   ├── cli/               # CLI commands
│   ├── context/           # Context management (shared, unified)
│   ├── memory/            # Memory system
│   ├── packages/          # Package manager
│   ├── protocols/mcp/     # MCP server
│   └── visualization/     # Trace visualization
├── tests/                 # Test suite
├── examples/              # Example scripts
└── docs/                  # Documentation
```

---

## Testing Commands

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/unit/test_shared_context.py -v

# Run with coverage
uv run pytest tests/ --cov=src/uacs --cov-report=html

# Type checking
uv run mypy src/uacs/ --ignore-missing-imports
```

---

## Common Development Tasks

### Install Dependencies
```bash
uv sync  # Install all dependencies from pyproject.toml
```

### Run CLI
```bash
uv run uacs --help
uv run uacs context stats
uv run uacs packages list
```

### Test Imports
```bash
uv run python -c "from uacs import UACS; print('✅ Import successful')"
```

### Build Package
```bash
uv build
```

---

## Key Technologies

- **Python 3.11+** - Core language
- **uv** - Package manager and virtual environment
- **Pydantic** - Data validation
- **FastAPI** - Web server
- **MCP** - Model Context Protocol
- **transformers** - Local LLM (TinyLlama) for tagging
- **pytest** - Testing framework

---

## Common Issues

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'uacs'`
**Solution:** Use `uv run python` instead of `python`

### Missing Dependencies
**Problem:** `ModuleNotFoundError: No module named 'transformers'`
**Solution:** `uv pip install transformers torch`

### Docker Tests Fail
**Problem:** Docker daemon not running
**Solution:** Expected - skip Docker tests if not needed

---

## Development Workflow

1. **Make changes** to src/uacs/
2. **Test imports**: `uv run python -c "from uacs import ..."`
3. **Run tests**: `uv run pytest tests/ -v`
4. **Check types**: `uv run mypy src/uacs/`
5. **Commit**: `git commit -m "..."`

---

## Recent Features (v0.2.0)

- ✅ Proactive compaction prevention for AI coding assistants
- ✅ Local LLM tagging via transformers (TinyLlama-1.1B)
- ✅ Trace visualization backend (Session/Event models)
- ✅ MCP server integration
- ⏳ Trace visualization frontend (pending)

---

## Documentation

- [Quick Start](./QUICKSTART.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Library Guide](./docs/LIBRARY_GUIDE.md)
- [CLI Reference](./docs/CLI_REFERENCE.md)
