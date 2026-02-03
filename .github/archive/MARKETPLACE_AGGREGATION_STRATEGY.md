# Marketplace Aggregation & Installation Strategy

**Product:** UACS (Universal Agent Context System)  
**Component:** `uacs/marketplace/`  
**Status:** Core Feature - Expansion planned in Phase 5.3  
**Timeline:** Phase 1 (Current - 2 sources), Phase 2 (Expansion to 5+ sources)  
**Date:** December 20, 2025 (Created), December 26, 2025 (Moved to UACS)

---

## Executive Summary

UACS aggregates existing agent capability marketplaces (Skills, MCP servers, AGENTS.md examples) and provides unified discovery, validation, and installation.

**Current Implementation (Phase 0):**
- ✅ 2 repository sources: Skills + MCP
- ✅ Unified search API
- ✅ Basic validation (format, structure)
- ✅ Installation to `.agent/skills/`

**Planned Expansion (Phase 5.3):**
- 📋 5+ marketplace sources (Smithery.ai, GitHub Topics, NPM, PyPI)
- 📋 Enhanced validation (security scanning, quality scoring)
- 📋 Multi-tool installation (Claude Desktop, Cursor, Cline, VS Code)
- 📋 Local cache with periodic sync

**Key Insight from Discussion:**
> "MCP Server - yes lots exist that is a benefit. our tool can find and connect to them and make them work with any agent."

**Strategy:** Aggregate existing marketplaces, don't compete. Be the universal installer and trust layer.

---

## The Value Proposition

### Real User Problem

**Before (Current State):**
1. Search GitHub for "python testing skill"
2. Find random repo
3. Copy-paste config manually
4. Test if it works (maybe)
5. Repeat for each tool (Claude Desktop, Cursor, Cline)
6. Hope it's secure
7. Forget to update

**After (With Multi-Agent Toolkit):**
```bash
$ multi-agent search "python testing"
$ multi-agent validate pytest-advanced
$ multi-agent install pytest-advanced --targets all
# Done. Works in Claude Desktop, Cursor, CLI
```

### Why This Matters

**Problem 1: Discovery is fragmented**
- Skills: Scattered across GitHub
- MCP servers: Multiple registries
- AGENTS.md: No central index
- Hard to compare options

**Problem 2: Trust is missing**
- No security validation
- No quality metrics
- Risky to install random packages
- No ratings or reviews

**Problem 3: Installation is manual**
- Different config for each tool
- Copy-paste errors
- Format differences
- Time-consuming

**Problem 4: Maintenance is neglected**
- No update notifications
- Don't know what's installed where
- Hard to remove unused packages

---

## Marketplaces to Aggregate

### Phase 1 (Launch - 3 Sources)

**1. Official MCP Registry**
- URL: https://modelcontextprotocol.io/servers
- Format: JSON listing
- Status: Official, well-maintained
- ~50 servers currently

**2. Agent Skills Repository**
- URL: Various GitHub repos (need to identify top ones)
- Format: SKILLS.md files
- Status: Community-driven
- Estimate: 100+ skills

**3. AGENTS.md Examples**
- URL: GitHub search, documentation sites
- Format: AGENTS.md files
- Status: Emerging standard
- Estimate: 50+ examples

### Phase 2 (Month 1 - Expand)

**4. Smithery.ai**
- MCP server registry
- Commercial + open source

**5. GitHub Topics**
- Search: `topic:mcp-server`
- Search: `topic:agent-skills`
- Dynamic discovery

**6. NPM Packages**
- Prefix: `@modelcontextprotocol/*`
- Published MCP servers

**7. PyPI Packages**
- Keywords: "mcp-server", "agent-skill"
- Python-based tools

### Phase 3 (Future - Community)

**8. User Submissions**
- Allow users to submit packages
- Moderation queue
- Community ratings

**9. Custom Registries**
- Organizations can host private registries
- Enterprise use case

---

## Aggregation Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Marketplace Aggregation System                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Source Adapters (Pluggable)                    │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  • MCPRegistryAdapter                           │  │
│  │  • GitHubSkillsAdapter                          │  │
│  │  • AgentsMdAdapter                              │  │
│  │  • SmitheryAdapter                              │  │
│  │  • NPMAdapter                                   │  │
│  │  • PyPIAdapter                                  │  │
│  └─────────────────────────────────────────────────┘  │
│                      │                                  │
│                      ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Unified Package Model                          │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  name, description, type, source                │  │
│  │  repository, stars, downloads                   │  │
│  │  last_updated, version                          │  │
│  │  dependencies, installation_targets             │  │
│  └─────────────────────────────────────────────────┘  │
│                      │                                  │
│                      ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Validation Pipeline                            │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  1. Security Scan (mcp-checkpoint)              │  │
│  │  2. Quality Check (code, docs, tests)           │  │
│  │  3. Dependency Audit                            │  │
│  │  4. Community Score (stars, reviews)            │  │
│  └─────────────────────────────────────────────────┘  │
│                      │                                  │
│                      ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Local Cache & Index                            │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  SQLite database                                │  │
│  │  ~/.multi-agent/marketplace.db                  │  │
│  │  Periodic sync (daily)                          │  │
│  └─────────────────────────────────────────────────┘  │
│                      │                                  │
│                      ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Installation Manager                           │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  • Claude Desktop installer                     │  │
│  │  • Cursor installer                             │  │
│  │  • Cline installer                              │  │
│  │  • VS Code installer                            │  │
│  │  • CLI installer                                │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Core Aggregation (Week 1-2)

**Task 1.1: Source Adapters**
```python
# src/multi_agent_cli/marketplace/adapters/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class Package:
    """Unified package model."""
    name: str
    description: str
    type: str  # "skill", "mcp-server", "agents-md"
    source: str  # "mcp-registry", "github", etc.
    repository: str
    stars: int
    downloads: int
    last_updated: str
    version: str
    dependencies: List[str]
    installation_targets: List[str]  # ["claude-desktop", "cursor", "cli"]
    security_score: float  # 0-100
    quality_score: float  # 0-100
    
class MarketplaceAdapter(ABC):
    """Base adapter for marketplace sources."""
    
    @abstractmethod
    async def search(self, query: str) -> List[Package]:
        """Search packages in this marketplace."""
        pass
    
    @abstractmethod
    async def get_package(self, name: str) -> Package:
        """Get specific package details."""
        pass
    
    @abstractmethod
    async def sync(self) -> List[Package]:
        """Sync all packages from source."""
        pass
```

**Task 1.2: MCP Registry Adapter**
```python
# src/multi_agent_cli/marketplace/adapters/mcp_registry.py
import httpx
from .base import MarketplaceAdapter, Package

class MCPRegistryAdapter(MarketplaceAdapter):
    """Adapter for official MCP registry."""
    
    BASE_URL = "https://modelcontextprotocol.io/api"
    
    async def search(self, query: str) -> List[Package]:
        """Search MCP registry."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/servers",
                params={"q": query}
            )
            data = response.json()
            
            return [
                Package(
                    name=item["name"],
                    description=item["description"],
                    type="mcp-server",
                    source="mcp-registry",
                    repository=item["repository"],
                    stars=item.get("stars", 0),
                    downloads=item.get("downloads", 0),
                    last_updated=item["updated_at"],
                    version=item["version"],
                    dependencies=item.get("dependencies", []),
                    installation_targets=["claude-desktop", "cursor", "cline"],
                    security_score=0.0,  # Calculate separately
                    quality_score=0.0,   # Calculate separately
                )
                for item in data["servers"]
            ]
    
    async def sync(self) -> List[Package]:
        """Sync entire registry."""
        # Fetch all pages
        # Store in local cache
        pass
```

**Task 1.3: GitHub Skills Adapter**
```python
# src/multi_agent_cli/marketplace/adapters/github_skills.py
import httpx
from .base import MarketplaceAdapter, Package

class GitHubSkillsAdapter(MarketplaceAdapter):
    """Adapter for GitHub agent skills."""
    
    # Known skills repositories
    KNOWN_REPOS = [
        "github.com/skills-repo-1",
        "github.com/skills-repo-2",
        # Add more as discovered
    ]
    
    async def search(self, query: str) -> List[Package]:
        """Search GitHub for skills."""
        # Use GitHub API
        # Search in known repos + topic:agent-skills
        pass
    
    async def sync(self) -> List[Package]:
        """Sync skills from known repos."""
        pass
```

**Task 1.4: Aggregation Manager**
```python
# src/multi_agent_cli/marketplace/manager.py
from typing import List
from .adapters import MCPRegistryAdapter, GitHubSkillsAdapter

class MarketplaceManager:
    """Manages all marketplace adapters."""
    
    def __init__(self):
        self.adapters = [
            MCPRegistryAdapter(),
            GitHubSkillsAdapter(),
            # Add more adapters
        ]
    
    async def search(self, query: str) -> List[Package]:
        """Search across all marketplaces."""
        results = []
        for adapter in self.adapters:
            try:
                packages = await adapter.search(query)
                results.extend(packages)
            except Exception as e:
                # Log error, continue with other adapters
                pass
        
        # Deduplicate and sort by relevance
        return self._deduplicate_and_rank(results, query)
    
    async def sync_all(self):
        """Sync all marketplaces to local cache."""
        for adapter in self.adapters:
            await adapter.sync()
```

### Phase 2: Validation System (Week 2-3)

**Task 2.1: Security Scanner Integration**
```python
# src/multi_agent_cli/marketplace/validation/security.py
from mcp_checkpoint import Scanner  # Use existing tool

class SecurityValidator:
    """Validates package security."""
    
    async def scan(self, package: Package) -> float:
        """
        Return security score 0-100.
        Uses mcp-checkpoint for MCP servers.
        """
        scanner = Scanner()
        
        # Clone repo temporarily
        repo_path = await self._clone_package(package)
        
        # Run security scan
        issues = await scanner.scan(repo_path)
        
        # Calculate score
        score = 100.0
        for issue in issues:
            if issue.severity == "critical":
                score -= 30
            elif issue.severity == "high":
                score -= 15
            elif issue.severity == "medium":
                score -= 5
        
        return max(0, score)
```

**Task 2.2: Quality Checker**
```python
# src/multi_agent_cli/marketplace/validation/quality.py

class QualityValidator:
    """Validates package quality."""
    
    async def check(self, package: Package) -> float:
        """Return quality score 0-100."""
        score = 0.0
        
        # Documentation (30 points)
        if await self._has_readme(package):
            score += 20
        if await self._has_examples(package):
            score += 10
        
        # Tests (30 points)
        if await self._has_tests(package):
            score += 20
        if await self._test_coverage(package) > 70:
            score += 10
        
        # Code quality (20 points)
        if await self._has_type_hints(package):
            score += 10
        if await self._passes_linter(package):
            score += 10
        
        # Community (20 points)
        if package.stars > 100:
            score += 10
        if package.downloads > 1000:
            score += 10
        
        return score
```

### Phase 3: Installation System (Week 3-4)

**Task 3.1: Claude Desktop Installer**
```python
# src/multi_agent_cli/marketplace/installers/claude_desktop.py
import json
from pathlib import Path

class ClaudeDesktopInstaller:
    """Installs packages to Claude Desktop."""
    
    CONFIG_PATH = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    
    async def install(self, package: Package):
        """Add package to Claude Desktop config."""
        config = self._load_config()
        
        if package.type == "mcp-server":
            config["mcpServers"][package.name] = {
                "command": self._get_command(package),
                "args": self._get_args(package),
                "env": self._get_env(package)
            }
        
        self._save_config(config)
        
        print(f"✓ Installed {package.name} to Claude Desktop")
        print("  Restart Claude Desktop to use it")
    
    async def uninstall(self, package_name: str):
        """Remove package from Claude Desktop."""
        config = self._load_config()
        
        if package_name in config["mcpServers"]:
            del config["mcpServers"][package_name]
            self._save_config(config)
            print(f"✓ Removed {package_name} from Claude Desktop")
    
    async def list_installed(self) -> List[str]:
        """List installed packages."""
        config = self._load_config()
        return list(config.get("mcpServers", {}).keys())
```

**Task 3.2: Universal Installer**
```python
# src/multi_agent_cli/marketplace/installers/manager.py

class InstallationManager:
    """Manages installation across multiple tools."""
    
    def __init__(self):
        self.installers = {
            "claude-desktop": ClaudeDesktopInstaller(),
            "cursor": CursorInstaller(),
            "cline": ClineInstaller(),
            "vscode": VSCodeInstaller(),
            "cli": CLIInstaller(),
        }
    
    async def install(
        self, 
        package: Package, 
        targets: List[str] = None
    ):
        """Install to specified targets."""
        if targets is None:
            targets = package.installation_targets
        
        for target in targets:
            if target in self.installers:
                await self.installers[target].install(package)
    
    async def list_installed(self, target: str = None) -> dict:
        """List installed packages by target."""
        if target:
            return {
                target: await self.installers[target].list_installed()
            }
        
        result = {}
        for name, installer in self.installers.items():
            result[name] = await installer.list_installed()
        return result
```

---

## CLI Commands

### Discovery Commands

```bash
# Search across all marketplaces
multi-agent search "python testing"
multi-agent search "code review" --type skill
multi-agent search "filesystem" --type mcp-server

# List available marketplaces
multi-agent marketplaces

# Sync marketplace data (daily auto-sync)
multi-agent sync

# Browse by category
multi-agent browse --category testing
multi-agent browse --category filesystem
```

### Validation Commands

```bash
# Validate before installing
multi-agent validate pytest-advanced

# Show detailed validation report
multi-agent validate pytest-advanced --detailed

# Validate multiple packages
multi-agent validate pytest-advanced pytest-mocking --compare
```

### Installation Commands

```bash
# Install to Claude Desktop (default)
multi-agent install pytest-advanced

# Install to specific tool
multi-agent install pytest-advanced --target cursor

# Install to multiple tools
multi-agent install pytest-advanced --targets claude-desktop,cursor,cli

# Install to all compatible tools
multi-agent install pytest-advanced --targets all

# Install with version
multi-agent install pytest-advanced@1.2.0
```

### Management Commands

```bash
# List installed packages
multi-agent list --installed

# List installed in specific tool
multi-agent list --installed --target claude-desktop

# Update package
multi-agent update pytest-advanced

# Update all packages
multi-agent update --all

# Uninstall package
multi-agent uninstall pytest-advanced

# Uninstall from specific tool
multi-agent uninstall pytest-advanced --target cursor
```

---

## User Experience Examples

### Example 1: Discover and Install

```bash
$ multi-agent search "python testing"

Found 8 results across 3 marketplaces:

┌────────────────────────────────────────────────────────┐
│ pytest-advanced (agent-skill) ⭐ 145  ✓ Validated     │
├────────────────────────────────────────────────────────┤
│ Advanced pytest patterns for Python testing            │
│ Repository: github.com/skills/pytest-advanced          │
│ Security: ✓ 100/100 (no vulnerabilities)              │
│ Quality: ✓ 87/100 (docs, tests, type hints)           │
│ Last updated: 2 days ago                               │
│ Downloads: 1,234                                       │
│ Compatible: claude-desktop, cursor, cline, cli         │
└────────────────────────────────────────────────────────┘

$ multi-agent install pytest-advanced --targets all

Installing pytest-advanced...
✓ Added to Claude Desktop config
✓ Added to Cursor config
✓ Added to Cline config
✓ Installed to CLI

Restart your tools to use pytest-advanced.
```

### Example 2: Validate Before Installing

```bash
$ multi-agent validate suspicious-package

Validating suspicious-package...

Security Scan:
✓ No hardcoded secrets
⚠️ 2 medium-severity vulnerabilities found
  - Outdated dependency: requests==2.25.0 (CVE-2021-33503)
  - Unvalidated file path in tool handler

Quality Check:
✓ Documentation: Complete (100%)
⚠️ Tests: Limited coverage (45%)
✓ Type hints: Present
✓ Linter: Passes

Community Score:
  Stars: 23 (low)
  Downloads: 45 (very low)
  Last updated: 6 months ago (stale)

Overall Risk: MEDIUM
Recommendation: Review vulnerabilities before installing

Install anyway? (y/N)
```

### Example 3: Manage Installed Packages

```bash
$ multi-agent list --installed

Installed packages across 3 tools:

Claude Desktop (3 packages):
┌────────────────────────────────────────────────┐
│ pytest-advanced                                │
│ Version: 1.2.0 (latest)                        │
│ Last updated: 2 days ago                       │
└────────────────────────────────────────────────┘

│ mcp-server-filesystem ⚠️ Update available      │
│ Version: 0.8.0 → 1.0.0 available               │
│ Update: multi-agent update mcp-server-filesystem│
└────────────────────────────────────────────────┘

Cursor (2 packages):
┌────────────────────────────────────────────────┐
│ pytest-advanced                                │
│ code-review-skill                              │
└────────────────────────────────────────────────┘

$ multi-agent update --all

Updating all packages...
✓ mcp-server-filesystem: 0.8.0 → 1.0.0
✓ All packages up to date
```

---

## Technical Considerations

### Caching Strategy

```python
# ~/.multi-agent/cache/
marketplace.db         # SQLite index of all packages
packages/             # Downloaded package configs
  └── pytest-advanced/
      ├── metadata.json
      └── SKILLS.md
```

**Sync Schedule:**
- Initial: On first run
- Auto: Daily at midnight
- Manual: `multi-agent sync`

### Deduplication

Packages may appear in multiple marketplaces. Dedupe by:
1. Repository URL (primary key)
2. Package name + author
3. Fingerprint of config file

### Security Considerations

**Validation Pipeline:**
1. mcp-checkpoint scan (for MCP servers)
2. Dependency vulnerability check (npm audit, pip-audit)
3. Malware scan (ClamAV or similar)
4. SAST (static analysis)

**Risk Levels:**
- ✅ **Safe**: No issues, high community score
- ⚠️ **Caution**: Minor issues, low community score
- ❌ **Risky**: Critical issues, unvalidated

**User Choice:**
- Can install risky packages with `--force`
- Clear warnings shown
- Audit trail logged

---

## Integration with Existing Features

### UACS Integration

Installed packages become available in UACS:
```python
# After installing pytest-advanced
uacs = UACS()
skills = uacs.get_available_skills()
# Now includes pytest-advanced
```

### MCP Server Exposure

Multi-agent toolkit itself exposed as MCP server:
```json
{
  "mcpServers": {
    "multi-agent": {
      "command": "multi-agent",
      "args": ["mcp-server"]
    }
  }
}
```

**Tools exposed:**
- `search_marketplace`
- `validate_package`
- `install_package`
- `list_installed`

---

## Success Metrics

### Phase 1 (Month 1)
- ✅ 3 marketplaces aggregated
- ✅ 100+ packages indexed
- ✅ Basic security validation working
- ✅ Install to Claude Desktop working
- ✅ 10 users installing packages

### Phase 2 (Month 2)
- ✅ 5+ marketplaces aggregated
- ✅ 300+ packages indexed
- ✅ Comprehensive validation pipeline
- ✅ Install to 4+ tools
- ✅ 50+ users, 500+ installs

### Phase 3 (Month 3)
- ✅ Community submissions enabled
- ✅ Rating/review system
- ✅ 1000+ packages indexed
- ✅ 200+ users
- ✅ Recognized as standard installer

---

## Competitive Moat

**Why this is defensible:**
1. **First-mover** - No good aggregator exists
2. **Validation data** - Accumulates over time
3. **Trust** - Hard to build, easy to lose
4. **Relationships** - With marketplace maintainers
5. **Network effects** - More users → better data → more users

**Not easy to copy:**
- Requires maintaining adapters for each format
- Security infrastructure investment
- Ongoing marketplace monitoring
- Community trust building

---

## Next Steps

1. ✅ Complete weekend launch (CLI + chat analyzer)
2. 🔨 Week 2: Build marketplace aggregation MVP
3. 🔨 Week 3: Add validation system
4. 🔨 Week 4: Add installation automation
5. 📢 Month 2: Public beta announcement

**Priority:** This is the core differentiator. Build after initial launch validation.
