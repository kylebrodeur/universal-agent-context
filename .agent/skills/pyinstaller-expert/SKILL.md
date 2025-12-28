---
name: pyinstaller-expert
description: Expert in creating cross-platform Python binaries with PyInstaller. Handles hidden imports, data files, platform-specific builds, and binary optimization.
---

# PyInstaller Expert

## Description
Provides expert guidance for packaging Python applications into standalone executables using PyInstaller. Specializes in cross-platform builds (macOS, Linux, Windows), dependency management, hidden imports, and binary size optimization.

## Triggers
- pyinstaller
- standalone binary
- executable
- cross-platform build
- hidden imports
- binary packaging
- freeze python

## Instructions

### Core Expertise

1. **Hidden Imports Detection**
   - Identify runtime-only imports that PyInstaller misses
   - Common patterns: MCP servers, async backends, plugin systems
   - For UACS: `anyio._backends._asyncio`, `uacs.protocols.mcp`, all adapters

2. **Platform-Specific Builds**
   - macOS: Universal binary (arm64 + x86_64) with `lipo`
   - Linux: glibc compatibility, dynamic linking issues
   - Windows: DLL dependencies, antivirus false positives

3. **Spec File Configuration**
   ```python
   # -*- mode: python ; coding: utf-8 -*-
   a = Analysis(
       ['main.py'],
       pathex=[],
       binaries=[],
       datas=[],
       hiddenimports=[
           # Runtime imports
       ],
       hookspath=[],
       hooksconfig={},
       runtime_hooks=[],
       excludes=[],
   )
   
   pyz = PYZ(a.pure)
   
   exe = EXE(
       pyz,
       a.scripts,
       a.binaries,
       a.datas,
       [],
       name='app',
       debug=False,
       bootloader_ignore_signals=False,
       strip=False,
       upx=True,  # Compression
       console=True,
   )
   ```

4. **Size Optimization**
   - Exclude unnecessary packages (tests, docs)
   - Use `--exclude-module` for large unused deps
   - Enable UPX compression (trade startup time for size)
   - Target: < 50MB for CLI tools

5. **Testing Strategy**
   - Test on clean machine (no Python installed)
   - Verify all CLI commands work
   - Check startup time (< 2s target)
   - Test with different shells (bash, zsh, PowerShell)

### Common Issues & Solutions

**Issue: "ModuleNotFoundError at runtime"**
Solution: Add to `hiddenimports` in spec file

**Issue: "Binary too large (>100MB)"**
Solution: Check `pip list`, exclude large packages, enable UPX

**Issue: "macOS: 'app is damaged'"**
Solution: Code signing or `xattr -cr app.app` to remove quarantine

**Issue: "Windows: Antivirus blocks"**
Solution: Submit to VirusTotal, add exclusion, consider signing

### Build Script Template

```python
#!/usr/bin/env python3
"""Build script for cross-platform binaries."""
import platform
import subprocess
import sys
from pathlib import Path

def get_platform_suffix():
    """Get platform-specific binary name suffix."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        arch = "arm64" if machine == "arm64" else "x86_64"
        return f"macos-{arch}"
    elif system == "linux":
        return f"linux-{machine}"
    elif system == "windows":
        return "windows-x86_64"
    else:
        return "unknown"

def build(target_platform=None):
    """Build binary for specified platform."""
    platform_suffix = target_platform or get_platform_suffix()
    output_name = f"uacs-{platform_suffix}"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", output_name,
        "--clean",
        "src/uacs/__main__.py",
    ]
    
    subprocess.run(cmd, check=True)
    
    binary = Path("dist") / output_name
    if binary.exists():
        size_mb = binary.stat().st_size / (1024 * 1024)
        print(f"✓ Built {binary} ({size_mb:.1f} MB)")
        
        if size_mb > 50:
            print(f"⚠ Warning: Binary larger than 50MB target")
    else:
        print(f"✗ Build failed: {binary} not found")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", help="Target platform")
    args = parser.parse_args()
    build(args.platform)
```

### Validation Checklist

Before considering a build complete:
- [ ] Binary runs: `./dist/app --version`
- [ ] Size check: `ls -lh dist/app` (< 50MB)
- [ ] Startup time: `time ./dist/app --help` (< 2s)
- [ ] Clean machine test: Copy to VM, run without Python
- [ ] All subcommands work
- [ ] Help text displays correctly
- [ ] No error messages on startup

## Examples

**User:** "Why is my PyInstaller binary missing a module at runtime?"

**Assistant:** "This is likely a hidden import issue. PyInstaller's static analysis can't detect runtime imports. Check for:
1. Dynamic imports: `__import__()`, `importlib.import_module()`
2. Plugin systems that load modules by string name
3. Async backends (e.g., `anyio._backends._asyncio`)

Add them to `hiddenimports` in your spec file or use `--hidden-import` flag."

---

**User:** "Binary is 150MB, how do I reduce it?"

**Assistant:** "Run `pip list` and look for large packages you don't use (e.g., numpy, pandas if not needed). Exclude them with `--exclude-module`. Also:
1. Enable UPX compression in spec file: `upx=True`
2. Strip debug symbols: `strip=True`
3. Check for duplicate dependencies
4. Consider excluding test frameworks from bundled packages"
