# Claude Code Context for UACS Project

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
├── .claude-plugin/        # Claude Code plugin (hooks)
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

## Claude Code Plugin

### Installation
```bash
cp .claude-plugin/plugin-proactive.json ~/.claude/plugin.json
cp .claude-plugin/hooks/*.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py
```

### Hooks
- `uacs_monitor_context.py` - Monitor context, compress at 50%
- `uacs_tag_prompt.py` - Tag prompts with local LLM (transformers)
- `uacs_inject_context.py` - Inject context on resume
- `uacs_store_realtime.py` - Real-time storage (crash-resistant)
- `uacs_precompact.py` - Emergency backup before compaction
- `uacs_store.py` - Final session storage

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

- ✅ Proactive compaction prevention for Claude Code
- ✅ Local LLM tagging via transformers (TinyLlama-1.1B)
- ✅ Trace visualization backend (Session/Event models)
- ✅ MCP server integration with plugin
- ⏳ Trace visualization frontend (pending)

---

## Documentation

- [Quick Start](./QUICKSTART.md)
- [Plugin Evolution](./.github/PLUGIN_EVOLUTION.md)
- [Compaction Prevention](./.github/COMPACTION_PREVENTION_STRATEGY.md)
- [Trace Visualization](./.github/TRACE_VISUALIZATION_DESIGN.md)
