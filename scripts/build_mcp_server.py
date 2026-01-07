#!/usr/bin/env python3
"""Build script for UACS MCP Server using PyInstaller."""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

def get_host_platform():
    """Detect the current host platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        if machine == "arm64":
            return "macos-arm64"
        return "macos-x86_64"
    elif system == "linux":
        return "linux-x86_64"
    elif system == "windows":
        return "windows-x86_64"
    return f"{system}-{machine}"

def build():
    """Build the MCP server binary."""
    parser = argparse.ArgumentParser(description="Build UACS MCP Server")
    parser.add_argument(
        "--platform", 
        choices=["macos-arm64", "macos-x86_64", "linux-x86_64", "windows-x86_64"],
        help="Target platform for the build. Defaults to host platform."
    )
    args_parsed = parser.parse_args()

    project_root = Path(__file__).parent.parent
    entry_point = project_root / "src" / "uacs" / "mcp_server_entry.py"
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    # Determine target platform
    target_platform = args_parsed.platform
    if not target_platform:
        target_platform = get_host_platform()
        print(f"No platform specified. Defaulting to host: {target_platform}")

    # Determine output name
    output_name = f"uacs-{target_platform}"
    if "windows" in target_platform and not output_name.endswith(".exe"):
        output_name += ".exe"

    print(f"Building UACS MCP Server for {target_platform}...")
    print(f"Output binary: {output_name}")

    # Check for cross-OS compilation issues
    host_os = platform.system().lower()
    target_os = "macos" if "macos" in target_platform else \
                "linux" if "linux" in target_platform else \
                "windows" if "windows" in target_platform else "unknown"
    
    host_os_mapped = "macos" if host_os == "darwin" else host_os

    if host_os_mapped != target_os:
        print(f"WARNING: Cross-compilation from {host_os_mapped} to {target_os} is not fully supported by PyInstaller.")
        print("This build may fail or produce a non-functional binary.")

    # Clean build directory (keep dist to allow accumulating multiple platform builds)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    # PyInstaller arguments
    pyinstaller_args = [
        "pyinstaller",
        f"--name={output_name}",
        "--onefile",
        "--clean",
        f"--paths={project_root}/src",
        # Add hidden imports if necessary (e.g., for dynamic imports)
        "--hidden-import=tiktoken_ext.openai_public",
        "--hidden-import=tiktoken_ext",
        str(entry_point)
    ]

    # Handle macOS target arch
    if host_os_mapped == "macos" and target_os == "macos":
        if "arm64" in target_platform:
            pyinstaller_args.append("--target-arch=arm64")
        elif "x86_64" in target_platform:
            pyinstaller_args.append("--target-arch=x86_64")

    try:
        # Suppress conda warnings by filtering stderr
        result = subprocess.run(
            pyinstaller_args, 
            check=True,
            capture_output=True,
            text=True
        )
        
        # Filter out conda warnings from output
        for line in result.stderr.split('\n'):
            if 'conda-meta' not in line and line.strip():
                print(line)
        
        print(f"\nBuild successful! Binary located at: {dist_dir / output_name}")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code {e.returncode}")
        if e.stderr:
            for line in e.stderr.split('\n'):
                if 'conda-meta' not in line and line.strip():
                    print(line)
        sys.exit(1)

if __name__ == "__main__":
    build()
