#!/bin/bash
# UACS Claude Code Plugin Installer
#
# This script installs the UACS plugin for automatic conversation storage
# in Claude Code sessions.

set -e

echo "🚀 Installing UACS Claude Code Plugin..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3.11+ required${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$PYTHON_VERSION < 3.11" | bc) -eq 1 ]]; then
    echo -e "${RED}❌ Python 3.11+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"

# Check Claude Code CLI
if ! command -v claude &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  Claude Code CLI not found"
    echo "   Install from: https://docs.anthropic.com/claude/docs/claude-code"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Claude Code CLI"
fi

# Install UACS Python package
echo ""
echo "📦 Installing UACS Python package..."

if command -v uv &> /dev/null; then
    echo "   Using uv (faster)..."
    uv pip install -e .
else
    echo "   Using pip..."
    pip install -e .
fi

echo -e "${GREEN}✓${NC} UACS package installed"

# Create plugin directory in current project
echo ""
echo "📁 Setting up plugin files..."

mkdir -p .claude/hooks
mkdir -p .claude/skills

# Copy plugin files
cp .claude-plugin/hooks/uacs_store.py .claude/hooks/
chmod +x .claude/hooks/uacs_store.py
echo -e "${GREEN}✓${NC} Hook script: .claude/hooks/uacs_store.py"

cp .claude-plugin/skills/uacs_context.md .claude/skills/
echo -e "${GREEN}✓${NC} Skill definition: .claude/skills/uacs_context.md"

cp .claude-plugin/plugin.json .claude/plugin.json
echo -e "${GREEN}✓${NC} Plugin manifest: .claude/plugin.json"

# Create .state directory for context storage
mkdir -p .state/context
echo -e "${GREEN}✓${NC} Storage directory: .state/context/"

# Test the hook script
echo ""
echo "🧪 Testing hook script..."

# Create mock transcript
MOCK_TRANSCRIPT=$(mktemp)
cat > "$MOCK_TRANSCRIPT" <<'EOF'
{"role": "user", "content": "Test message"}
{"role": "assistant", "content": "Test response"}
EOF

# Test hook
HOOK_INPUT=$(cat <<EOF
{
  "transcript_path": "$MOCK_TRANSCRIPT",
  "session_id": "test-install",
  "project_dir": "."
}
EOF
)

HOOK_RESULT=$(echo "$HOOK_INPUT" | python3 .claude/hooks/uacs_store.py)
if echo "$HOOK_RESULT" | grep -q '"continue": true'; then
    echo -e "${GREEN}✓${NC} Hook test passed"
else
    echo -e "${RED}❌ Hook test failed${NC}"
    echo "$HOOK_RESULT"
    rm "$MOCK_TRANSCRIPT"
    exit 1
fi

rm "$MOCK_TRANSCRIPT"

# Success
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ UACS Plugin Installed Successfully!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 What happens now:"
echo "   • Every Claude Code session is automatically stored"
echo "   • Stored in: .state/context/ (100% fidelity)"
echo "   • Organized by topics (security, performance, etc.)"
echo "   • Deduplication saves ~15% tokens"
echo ""
echo "🎯 Next steps:"
echo "   1. Start Claude Code: ${YELLOW}claude${NC}"
echo "   2. Have a conversation (it's automatically stored!)"
echo "   3. Check storage: ${YELLOW}ls .state/context/${NC}"
echo "   4. Optional: Start MCP server for retrieval:"
echo "      ${YELLOW}uacs serve${NC}"
echo ""
echo "📖 Documentation:"
echo "   • Hook details: .claude-plugin/hooks/uacs_store.py"
echo "   • Skill guide: .claude-plugin/skills/uacs_context.md"
echo "   • Full docs: README.md"
echo ""
echo "💡 Tip: To search stored conversations:"
echo "   ${YELLOW}@uacs_search_context query=\"security issues\"${NC}"
echo ""
echo "🎉 Happy coding with perfect context recall!"
echo ""
