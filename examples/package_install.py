"""
Example: Package Installation and Management

This script demonstrates how to use the UACS package manager to:
- Install packages from GitHub, Git URLs, or local paths
- List installed packages
- Validate packages
- Uninstall packages
"""

import sys
from pathlib import Path

# Ensure we can import uacs from src
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uacs.packages import PackageManager, PackageSource


def main():
    print("📦 UACS Package Manager Example\n")
    print("=" * 70)

    # Initialize package manager
    print("\n🔧 Initializing PackageManager...")
    manager = PackageManager(Path.cwd())
    print(f"   Packages directory: {manager.skills_dir}")

    # Example 1: Install from GitHub
    print("\n" + "=" * 70)
    print("Example 1: Installing from GitHub")
    print("=" * 70)

    github_source = "anthropic/skills-example"
    print(f"\n📥 Installing from GitHub: {github_source}")
    print("   Format: owner/repo")
    print(f"   Full URL: https://github.com/{github_source}.git\n")

    try:
        print("   ⏳ Fetching package...")
        package = manager.install(github_source)

        print(f"   ✅ Installation successful!")
        print(f"      Name: {package.name}")
        print(f"      Source: {package.source}")
        print(f"      Type: {package.source_type.value}")
        print(f"      Location: {package.location}")
        if package.version:
            print(f"      Version: {package.version}")

    except Exception as e:
        print(f"   ⚠️  Installation would require: {e}")
        print("   (This is expected if the repository doesn't exist)")

    # Example 2: Install from Git URL
    print("\n" + "=" * 70)
    print("Example 2: Installing from Git URL")
    print("=" * 70)

    git_url = "https://github.com/anthropic/skills-example.git"
    print(f"\n📥 Installing from Git URL: {git_url}")
    print("   Supported formats:")
    print("   - https://github.com/owner/repo.git")
    print("   - https://gitlab.com/group/project.git")
    print("   - git@github.com:owner/repo.git\n")

    print("   (Skipping actual installation - requires valid repository)")

    # Example 3: Install from local path
    print("\n" + "=" * 70)
    print("Example 3: Installing from Local Path")
    print("=" * 70)

    local_path = "/path/to/local/skill"
    print(f"\n📥 Installing from local path: {local_path}")
    print("   Usage: manager.install('/absolute/path/to/skill')")
    print("   Note: Path must exist and contain valid SKILL.md\n")

    # Example 4: List installed packages
    print("\n" + "=" * 70)
    print("Example 4: List Installed Packages")
    print("=" * 70)

    print("\n📋 Getting list of installed packages...")
    packages = manager.list_installed()

    if packages:
        print(f"\n✅ Found {len(packages)} installed packages:\n")
        for pkg in packages:
            status = "✓" if pkg.is_valid else "✗"
            print(f"   {status} {pkg.name}")
            print(f"      Source: {pkg.source}")
            print(f"      Type: {pkg.source_type.value}")
            print(f"      Location: {pkg.location}")
            if pkg.version:
                print(f"      Version: {pkg.version}")
            print()
    else:
        print("\n   No packages installed yet.\n")

    # Example 5: Validate a package
    print("\n" + "=" * 70)
    print("Example 5: Validate Package")
    print("=" * 70)

    print("\n✔️  Validating packages...")
    if packages:
        pkg_name = packages[0].name
        print(f"\n   Validating: {pkg_name}")
        try:
            result = manager.validate(pkg_name)
            if result.valid:
                print(f"   ✅ Package is valid")
                if result.metadata:
                    print(f"      Name: {result.metadata.get('name', 'N/A')}")
                    print(f"      Description: {result.metadata.get('description', 'N/A')}")
                    print(f"      Version: {result.metadata.get('version', 'N/A')}")
            else:
                print(f"   ❌ Validation failed:")
                for error in result.errors:
                    print(f"      {error.field}: {error.message}")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    else:
        print("\n   No packages to validate.\n")

    # Example 6: Supported source types
    print("\n" + "=" * 70)
    print("Example 6: Supported Package Sources")
    print("=" * 70)

    print("\n🌐 PackageManager supports three source types:\n")

    sources_info = [
        (
            "GitHub Shorthand",
            "anthropic/skills-example",
            "Quick reference for public GitHub repositories",
        ),
        (
            "Git URL",
            "https://github.com/anthropic/skills-example.git",
            "Full URLs for GitHub, GitLab, or custom Git hosts",
        ),
        (
            "Local Path",
            "/home/user/my-skill",
            "Absolute paths to local skill directories",
        ),
    ]

    for i, (name, example, description) in enumerate(sources_info, 1):
        print(f"   {i}. {name}")
        print(f"      Example: {example}")
        print(f"      {description}\n")

    # Example 7: Package manager operations
    print("\n" + "=" * 70)
    print("Example 7: Common Package Manager Operations")
    print("=" * 70)

    print("""
Available operations:

1. Install a package:
   package = manager.install("owner/repo")
   print(f"Installed: {package.name}")

2. List all installed:
   packages = manager.list_installed()
   for pkg in packages:
       print(f"- {pkg.name} from {pkg.source}")

3. Validate a package:
   result = manager.validate("package-name")
   if result.valid:
       print("Package is valid!")

4. Uninstall a package:
   success = manager.uninstall("package-name")
   print(f"Uninstalled: {success}")

5. Update a package (GitHub/Git sources only):
   updated_pkg = manager.update("package-name")
   print(f"Updated: {updated_pkg.name}")

6. Get package location:
   for pkg in manager.list_installed():
       with open(pkg.location / "SKILL.md") as f:
           content = f.read()
    """)

    # Example 8: Error handling
    print("\n" + "=" * 70)
    print("Example 8: Error Handling")
    print("=" * 70)

    print("""
Common errors and solutions:

1. PackageManagerError - Invalid source format:
   Supported formats:
   - owner/repo (GitHub)
   - https://... (Git URL)
   - /path/to/skill (Local path)

2. PackageManagerError - Package already installed:
   Use update() to upgrade or uninstall() then install() to reinstall

3. PackageManagerError - Local path does not exist:
   Verify the path exists and contains SKILL.md

4. PackageManagerError - Package validation failed:
   Ensure SKILL.md exists and contains required metadata

5. PackageManagerError - Cannot update local packages:
   Local packages don't track source - uninstall and reinstall instead
    """)

    # Summary
    print("\n" + "=" * 70)
    print("✅ Package Manager Example Complete")
    print("=" * 70)

    print(f"\nPackages stored in: {manager.skills_dir}")
    print(f"Metadata file: {manager.metadata_file}")
    print("\nFor more details, see src/uacs/packages/manager.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
