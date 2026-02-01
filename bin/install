#!/bin/bash
# UACS MCP Server Installation Script for macOS
# Installs the standalone binary to /usr/local/bin

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect platform
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

echo "🚀 UACS MCP Server Installation"
echo "================================"
echo ""
echo "Platform: $PLATFORM"
echo "Architecture: $ARCH"
echo ""

# Validate platform
if [ "$PLATFORM" != "darwin" ]; then
    echo -e "${RED}Error: This script is for macOS only.${NC}"
    echo "For other platforms, please download the appropriate binary from:"
    echo "https://github.com/kylebrodeur/universal-agent-context/releases"
    exit 1
fi

# Validate architecture
if [ "$ARCH" != "arm64" ] && [ "$ARCH" != "x86_64" ]; then
    echo -e "${RED}Error: Unsupported architecture: $ARCH${NC}"
    exit 1
fi

# Determine binary name
if [ "$ARCH" == "arm64" ]; then
    BINARY_NAME="uacs-macos-arm64"
else
    BINARY_NAME="uacs-macos-x86_64"
fi

# Check if binary exists locally (for local installations)
LOCAL_BINARY="./dist/$BINARY_NAME"
INSTALL_DIR="/usr/local/bin"
TARGET_NAME="uacs-mcp"

if [ -f "$LOCAL_BINARY" ]; then
    echo -e "${GREEN}✓${NC} Found local binary: $LOCAL_BINARY"
    BINARY_SOURCE="$LOCAL_BINARY"
else
    echo -e "${YELLOW}⚠${NC}  Local binary not found. In the future, this will download from GitHub Releases."
    echo ""
    echo "For now, please:"
    echo "1. Build the binary: uv run python scripts/build_mcp_server.py"
    echo "2. Run this script again"
    exit 1
fi

# Check if install directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠${NC}  $INSTALL_DIR does not exist. Creating..."
    sudo mkdir -p "$INSTALL_DIR"
fi

# Copy binary to install directory
echo ""
echo "Installing to $INSTALL_DIR/$TARGET_NAME..."
if sudo cp "$BINARY_SOURCE" "$INSTALL_DIR/$TARGET_NAME"; then
    echo -e "${GREEN}✓${NC} Binary copied successfully"
else
    echo -e "${RED}✗${NC} Failed to copy binary"
    exit 1
fi

# Make executable
if sudo chmod +x "$INSTALL_DIR/$TARGET_NAME"; then
    echo -e "${GREEN}✓${NC} Made executable"
else
    echo -e "${RED}✗${NC} Failed to make executable"
    exit 1
fi

# On macOS, remove quarantine attribute if present
if command -v xattr &> /dev/null; then
    sudo xattr -d com.apple.quarantine "$INSTALL_DIR/$TARGET_NAME" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Removed quarantine attribute"
fi

# Test installation
echo ""
echo "Testing installation..."
if "$INSTALL_DIR/$TARGET_NAME" --help &> /dev/null; then
    echo -e "${GREEN}✓${NC} Installation successful!"
else
    echo -e "${RED}✗${NC} Installation test failed"
    exit 1
fi

echo ""
echo "================================"
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "You can now run the MCP server with:"
echo "  $TARGET_NAME --transport sse --port 3000"
echo ""
echo "For stdio mode (Claude Desktop):"
echo "  $TARGET_NAME --transport stdio"
echo ""
echo "To configure Claude Desktop, add to your config:"
echo '  "uacs": {'
echo '    "command": "'$INSTALL_DIR/$TARGET_NAME'",'
echo '    "args": ["--transport", "stdio"]'
echo '  }'
echo ""
