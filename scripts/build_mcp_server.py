#!/usr/bin/env python3
"""Build script for UACS MCP Server using PyInstaller."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def build():
    """Build the MCP server binary."""
    project_root = Path(__file__).parent.parent
    entry_point = project_root / "src" / "uacs" / "mcp_server_entry.py"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    print(f"Building UACS MCP Server from {entry_point}...")
    
    # Clean previous builds
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
        
    # PyInstaller arguments
    args = [
        "pyinstaller",
        "--name=uacs-mcp-server",
        "--onefile",
        "--clean",
        f"--paths={project_root}/src",
        # Add hidden imports if necessary (e.g., for dynamic imports)
        "--hidden-import=tiktoken_ext.openai_public",
        "--hidden-import=tiktoken_ext",
        str(entry_point)
    ]
    
    try:
        subprocess.run(args, check=True)
        print(f"\nBuild successful! Binary located at: {dist_dir / 'uacs-mcp-server'}")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    build()
