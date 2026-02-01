# UACS Security Guide

**Last Updated:** December 26, 2025  
**Status:** Phase 6.1 Implementation Guide  
**Applies to:** UACS (Universal Agent Context System) only

---

## Overview

This guide covers security best practices for UACS components:
- Context management (shared context, compression)
- Package management (discovery, validation, installation)
- MCP server (Model Context Protocol implementation)
- Memory system (persistent storage)

**Note:** For orchestration security (multi-agent coordination, agent servers), see [MAOS Security Documentation](https://github.com/kylebrodeur/multi-agent-cli/blob/main/docs/future/SECURITY_IMPLEMENTATION_PLAN.md).

---

## Security Architecture

### Threat Model

**UACS handles:**
1. **User-provided context** - Skills, project metadata, memory entries
2. **Packages** - Third-party skills and MCP servers
3. **MCP server operations** - File system access, tool execution
4. **Memory storage** - Persistent data across sessions

**Attack Vectors:**
- Prompt injection via malicious context
- Command injection via MCP tools
- Path traversal in file operations
- Secrets in installed packages
- Malicious code in installed skills

---

## Phase 6.1: Input Validation (UACS-Specific)

### 1. Context Management Security

**Component:** `uacs/context/shared_context.py`, `uacs/context/unified_context.py`

**Threats:**
- Prompt injection in shared context entries
- Malicious content in compression summaries
- Secrets leaked in context history

**Mitigations:**

```python
# uacs/security/validator.py (to be created)
from typing import Dict, Any
import re

class ContextValidator:
    """Validates context entries for security threats."""
    
    # Patterns that indicate potential prompt injection
    SUSPICIOUS_PATTERNS = [
        r"ignore\s+all\s+previous\s+instructions",
        r"disregard\s+.*\s+above",
        r"system:\s*you\s+are\s+now",
        r"<\s*system\s*>",
        r"\\x[0-9a-fA-F]{2}",  # Hex encoding attempts
    ]
    
    def validate_context_entry(self, content: str) -> tuple[bool, str]:
        """
        Validate context entry for security issues.
        
        Returns:
            (is_valid, reason)
        """
        # Check for prompt injection patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return False, f"Potential prompt injection detected: {pattern}"
        
        # Check for secrets (basic patterns)
        if self._contains_secrets(content):
            return False, "Potential secret detected in context"
        
        return True, "Valid"
    
    def _contains_secrets(self, text: str) -> bool:
        """Check for common secret patterns."""
        secret_patterns = [
            r"[a-zA-Z0-9]{32,}",  # API keys (loose pattern)
            r"sk-[a-zA-Z0-9]{32,}",  # OpenAI keys
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub tokens
            r"AIzaSy[a-zA-Z0-9_-]{33}",  # Google API keys
        ]
        for pattern in secret_patterns:
            if re.search(pattern, text):
                return True
        return False
```

**Integration:**

```python
# In uacs/context/shared_context.py
from uacs.security.validator import ContextValidator

class SharedContextManager:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.validator = ContextValidator()
    
    def add_entry(self, content: str, agent: str, **kwargs) -> None:
        """Add context entry with validation."""
        is_valid, reason = self.validator.validate_context_entry(content)
        if not is_valid:
            logger.warning(f"Context validation failed: {reason}")
            # Option 1: Reject
            raise SecurityError(f"Invalid context: {reason}")
            # Option 2: Sanitize and warn (future enhancement)
```

### 2. Package Management Security

**Component:** `uacs/packages/manager.py`

**Threats:**
- Malicious code in skill files
- Secrets hardcoded in package metadata
- Dependency vulnerabilities
- Supply chain attacks

**Mitigations:**

```python
# uacs/security/package_scanner.py (to be created)
import re
from pathlib import Path
from typing import Dict, List

class PackageSecurityScanner:
    """Scans marketplace packages for security issues."""
    
    def scan_package(self, package_path: Path) -> Dict[str, Any]:
        """
        Scan package for security vulnerabilities.
        
        Returns:
            {
                "safe": bool,
                "issues": List[str],
                "score": float  # 0-100
            }
        """
        issues = []
        
        # 1. Scan for hardcoded secrets
        secrets = self._scan_secrets(package_path)
        if secrets:
            issues.append(f"Found {len(secrets)} potential secrets")
        
        # 2. Check for dangerous commands
        dangerous_cmds = self._scan_dangerous_commands(package_path)
        if dangerous_cmds:
            issues.append(f"Found {len(dangerous_cmds)} dangerous commands")
        
        # 3. Validate file permissions
        if self._has_executable_files(package_path):
            issues.append("Package contains executable files")
        
        # Calculate score (100 - 20 per issue, min 0)
        score = max(0, 100 - (len(issues) * 20))
        safe = score >= 80
        
        return {
            "safe": safe,
            "issues": issues,
            "score": score
        }
    
    def _scan_secrets(self, path: Path) -> List[str]:
        """Scan files for hardcoded secrets."""
        secrets = []
        for file in path.rglob("*.py"):
            content = file.read_text()
            # Check for API key patterns
            if re.search(r'["\']?[A-Z0-9]{32,}["\']?', content):
                secrets.append(str(file))
        return secrets
    
    def _scan_dangerous_commands(self, path: Path) -> List[str]:
        """Scan for dangerous command patterns."""
        dangerous = []
        patterns = [
            r'subprocess\.(?:call|run|Popen)',
            r'os\.system',
            r'eval\(',
            r'exec\(',
            r'__import__',
        ]
        for file in path.rglob("*.py"):
            content = file.read_text()
            for pattern in patterns:
                if re.search(pattern, content):
                    dangerous.append(f"{file}: {pattern}")
        return dangerous
    
    def _has_executable_files(self, path: Path) -> bool:
        """Check if package contains executable files."""
        for file in path.rglob("*"):
            if file.is_file() and file.stat().st_mode & 0o111:
                return True
        return False
```

**Integration:**

```python
# In uacs/packages/manager.py
from uacs.security.package_scanner import PackageSecurityScanner

class PackageManager:
    def __init__(self):
        self.scanner = PackageSecurityScanner()

    def install(self, package: Package, target_dir: Path) -> Dict:
        """Install package with security validation."""
        # Download/extract package to temp location
        temp_path = self._download_package(package)

        # Security scan BEFORE installation
        scan_result = self.scanner.scan_package(temp_path)

        if not scan_result["safe"]:
            raise SecurityError(
                f"Package failed security scan (score: {scan_result['score']}): "
                f"{', '.join(scan_result['issues'])}"
            )

        # If scan passes, proceed with installation
        return self._install_to_target(temp_path, target_dir)
```

### 3. MCP Server Security

**Component:** `uacs/protocols/mcp/skills_server.py`

**Threats:**
- Path traversal in file operations
- Command injection via tool arguments
- Resource exhaustion (DoS)
- Unauthorized access to sensitive files

**Mitigations:**

```python
# uacs/security/mcp_security.py (to be created)
from pathlib import Path
import re

class MCPSecurityGuard:
    """Security guard for MCP server operations."""
    
    def __init__(self, allowed_paths: List[Path]):
        self.allowed_paths = [p.resolve() for p in allowed_paths]
    
    def validate_file_path(self, requested_path: str) -> Path:
        """
        Validate file path to prevent path traversal.
        
        Raises:
            SecurityError if path is outside allowed directories
        """
        # Resolve to absolute path
        path = Path(requested_path).resolve()
        
        # Check if within allowed paths
        for allowed in self.allowed_paths:
            try:
                path.relative_to(allowed)
                return path
            except ValueError:
                continue
        
        raise SecurityError(
            f"Path {path} is outside allowed directories: {self.allowed_paths}"
        )
    
    def sanitize_tool_arguments(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize tool arguments to prevent injection.
        
        Returns:
            Sanitized arguments
        """
        sanitized = {}
        for key, value in args.items():
            if isinstance(value, str):
                # Remove shell metacharacters
                value = re.sub(r'[;&|`$(){}[\]<>]', '', value)
            sanitized[key] = value
        return sanitized
    
    def check_rate_limit(self, client_id: str, operation: str) -> bool:
        """
        Check if client has exceeded rate limit.
        
        Returns:
            True if allowed, False if rate limited
        """
        # TODO: Implement rate limiting with token bucket or sliding window
        # For Phase 6.1, log only
        logger.debug(f"Rate limit check: {client_id} - {operation}")
        return True
```

**Integration:**

```python
# In uacs/protocols/mcp/skills_server.py
from uacs.security.mcp_security import MCPSecurityGuard

class SkillsMCPServer:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.security = MCPSecurityGuard(
            allowed_paths=[project_path, project_path / ".agent"]
        )
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict) -> Any:
        """Handle tool call with security validation."""
        # Sanitize arguments
        safe_args = self.security.sanitize_tool_arguments(arguments)
        
        # Validate file paths if present
        if "path" in safe_args:
            safe_args["path"] = self.security.validate_file_path(safe_args["path"])
        
        # Check rate limit
        client_id = self._get_client_id()
        if not self.security.check_rate_limit(client_id, tool_name):
            raise SecurityError("Rate limit exceeded")
        
        # Execute tool with sanitized arguments
        return await self._execute_tool(tool_name, safe_args)
```

### 4. Memory System Security

**Component:** `uacs/memory/simple_memory.py`

**Threats:**
- Sensitive data in memory entries
- Unauthorized access to global memory
- Memory injection attacks

**Mitigations:**

```python
# Memory entries should be validated before storage
class SimpleMemoryStore:
    def __init__(self, project_path: Path, global_path: Path | None = None):
        self.project_path = project_path
        self.global_path = global_path
        self.validator = ContextValidator()  # Reuse context validator
    
    def add_memory(self, content: str, tags: List[str], scope: str = "project") -> None:
        """Add memory with validation."""
        # Validate content
        is_valid, reason = self.validator.validate_context_entry(content)
        if not is_valid:
            logger.warning(f"Memory validation failed: {reason}")
            raise SecurityError(f"Invalid memory content: {reason}")
        
        # Store memory
        entry = MemoryEntry(content=content, tags=tags, scope=scope)
        self._persist(entry, scope)
```

---

## Optional: MCP Checkpoint Integration

**Tool:** [aira-security/mcp-checkpoint](https://github.com/aira-security/mcp-checkpoint)

**Use Cases for UACS:**
- Baseline drift detection for MCP server configurations
- Automated vulnerability scanning for installed packages
- Prompt injection detection (ML-based)

**Evaluation Checklist:**
- [ ] Review mcp-checkpoint source code
- [ ] Test in isolated environment
- [ ] Measure false positive rate
- [ ] Assess performance impact
- [ ] Document integration steps

**If Adopted:**

```bash
# Install
pip install mcp-checkpoint

# Scan MCP configuration
mcp-checkpoint inspect

# Create baseline
mcp-checkpoint baseline create

# Detect drift
mcp-checkpoint baseline check
```

---

## Security Best Practices

### For Users

1. **Review packages before installation:**
   ```bash
   # Check package metadata
   uacs packages info package-name

   # View package source (if available)
   uacs packages inspect package-name
   ```

2. **Use project-scoped memory for sensitive data:**
   ```bash
   # Project memory stays in .state/memory/
   uacs memory add "API key: ..." --scope project
   
   # Avoid global memory for secrets
   ```

3. **Limit MCP server file access:**
   ```bash
   # Start MCP server with restricted path
   uacs serve --allowed-paths ./src ./docs
   ```

### For Developers

1. **Always validate user input:**
   - Use `ContextValidator` for context entries
   - Use `PackageSecurityScanner` before installation
   - Use `MCPSecurityGuard` for file operations

2. **Never log secrets:**
   ```python
   # BAD
   logger.info(f"Using API key: {api_key}")
   
   # GOOD
   logger.info("Using API key: [REDACTED]")
   ```

3. **Use secure defaults:**
   - Enable validation by default
   - Require explicit opt-in for dangerous operations
   - Fail closed (reject on validation failure)

4. **Implement defense in depth:**
   - Input validation (first line)
   - Sandboxing (second line)
   - Audit logging (detection)
   - Rate limiting (DoS prevention)

---

## Security Configuration

**Environment Variables:**

```bash
# Enable strict validation (default: true)
UACS_STRICT_VALIDATION=true

# Enable security logging (default: false)
UACS_SECURITY_LOGGING=true

# Set security log path
UACS_SECURITY_LOG=.state/security/security.log

# MCP server rate limiting (requests per minute)
UACS_MCP_RATE_LIMIT=100
```

**Configuration File:** `.uacs/security.json`

```json
{
  "validation": {
    "strict_mode": true,
    "reject_on_secrets": true,
    "reject_on_injection": true
  },
  "package_management": {
    "scan_before_install": true,
    "min_security_score": 80,
    "allow_executables": false
  },
  "mcp_server": {
    "rate_limit_rpm": 100,
    "allowed_paths": ["./src", "./docs"],
    "enable_audit_log": true
  }
}
```

---

## Reporting Security Vulnerabilities

**Email:** security@[your-domain].com  
**PGP Key:** [Link to public key]

**What to Include:**
1. Description of vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

**Response Time:**
- Acknowledgment: 24 hours
- Initial assessment: 48 hours
- Fix timeline: Varies by severity

**Disclosure Policy:**
- Critical: Immediate fix + disclosure after patch
- High: Fix within 7 days + disclosure after 14 days
- Medium: Fix within 30 days + public disclosure
- Low: Fix in next release

---

## Security Checklist (Phase 6.1)

**Implementation:**
- [ ] Create `uacs/security/` module
- [ ] Implement `ContextValidator` class
- [ ] Implement `PackageSecurityScanner` class
- [ ] Implement `MCPSecurityGuard` class
- [ ] Integrate validation in `SharedContextManager`
- [ ] Integrate scanning in `PackageManager`
- [ ] Integrate security guard in MCP server
- [ ] Add validation to `SimpleMemoryStore`
- [ ] Write 50+ security tests
- [ ] Document security configuration options
- [ ] Create security policy (SECURITY.md)

**Testing:**
- [ ] Test prompt injection detection
- [ ] Test secret detection in packages
- [ ] Test path traversal prevention
- [ ] Test command injection prevention
- [ ] Test rate limiting
- [ ] Perform security audit with `bandit`
- [ ] Check dependencies with `safety` and `pip-audit`

**Documentation:**
- [x] Create SECURITY.md guide (this file)
- [ ] Add security section to README
- [ ] Document security configuration
- [ ] Create security best practices guide
- [ ] Add security examples

---

## References

- [OWASP Top 10 for LLMs](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/security)
- [MAOS Security Implementation](https://github.com/kylebrodeur/multi-agent-cli/blob/main/docs/future/SECURITY_IMPLEMENTATION_PLAN.md)
- [UACS Development Roadmap](../.github/internal/DEVELOPMENT_ROADMAP.md)

---

**Last Updated:** December 26, 2025  
**Next Review:** End of Phase 6.1 implementation
