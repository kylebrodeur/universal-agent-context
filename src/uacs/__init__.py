"""Universal Agent Context System (UACS)

Provides unified context management for AI agents:
- Marketplace discovery (Skills + MCP)
- Format adapters (Agent Skills, AGENTS.md, etc.)
- Context management (shared memory + compression)
- Semantic conversations and knowledge (v0.3.0+)

Example:
    >>> from uacs import UACS
    >>> from pathlib import Path
    >>>
    >>> uacs = UACS(project_path=Path("."))
    >>>
    >>> # Package management
    >>> uacs.install_package("owner/repo")
    >>>
    >>> # Semantic conversation tracking (v0.3.0+)
    >>> uacs.add_user_message("Help with auth", turn=1, session_id="s1")
    >>> uacs.add_decision("Use JWT", rationale="Stateless", session_id="s1")
    >>>
    >>> # Natural language search across all context
    >>> results = uacs.search("how did we implement authentication?")
"""

from uacs.api import UACS

__version__ = "0.3.0-dev"
__all__ = ["UACS"]
