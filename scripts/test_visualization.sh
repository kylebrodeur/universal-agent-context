#!/bin/bash
# Test script for UACS Context Graph Visualizer
# This script verifies that all components are properly installed and functional

set -e  # Exit on error

echo "=================================================="
echo "UACS Context Graph Visualizer - Verification Test"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track status
ALL_PASSED=true

# Test 1: Check Python files exist
echo -e "${YELLOW}[1/7] Checking file structure...${NC}"
FILES=(
    "src/uacs/visualization/__init__.py"
    "src/uacs/visualization/web_server.py"
    "src/uacs/visualization/visualization.py"
    "src/uacs/visualization/static/index.html"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo -e "  ${RED}✗ Missing: $file${NC}"
        ALL_PASSED=false
    fi
done
echo ""

# Test 2: Check dependencies in pyproject.toml
echo -e "${YELLOW}[2/7] Checking dependencies...${NC}"
DEPS=("fastapi" "websockets" "uvicorn")

for dep in "${DEPS[@]}"; do
    if grep -q "$dep" pyproject.toml; then
        echo "  ✓ $dep found in pyproject.toml"
    else
        echo -e "  ${RED}✗ Missing dependency: $dep${NC}"
        ALL_PASSED=false
    fi
done
echo ""

# Test 3: Check imports
echo -e "${YELLOW}[3/7] Verifying Python imports...${NC}"
python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from uacs.visualization import ContextVisualizer, VisualizationServer
    print('  ✓ ContextVisualizer imported')
    print('  ✓ VisualizationServer imported')
except ImportError as e:
    print(f'  ✗ Import error: {e}')
    sys.exit(1)
" || ALL_PASSED=false
echo ""

# Test 4: Check CLI integration
echo -e "${YELLOW}[4/7] Checking CLI integration...${NC}"
if grep -q "with_ui" src/uacs/cli/main.py; then
    echo "  ✓ --with-ui flag found in CLI"
else
    echo -e "  ${RED}✗ --with-ui flag not found${NC}"
    ALL_PASSED=false
fi
echo ""

# Test 5: Check documentation
echo -e "${YELLOW}[5/7] Checking documentation...${NC}"
DOCS=(
    "docs/VISUALIZATION.md"
    "docs/VISUALIZATION_QUICKSTART.md"
    "src/uacs/visualization/README.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "  ✓ $doc"
    else
        echo -e "  ${RED}✗ Missing: $doc${NC}"
        ALL_PASSED=false
    fi
done
echo ""

# Test 6: Check tests
echo -e "${YELLOW}[6/7] Checking test files...${NC}"
if [ -f "tests/test_visualization_server.py" ]; then
    echo "  ✓ tests/test_visualization_server.py"
    # Count test functions
    TEST_COUNT=$(grep -c "^def test_" tests/test_visualization_server.py || echo "0")
    echo "  ✓ Found $TEST_COUNT test functions"
else
    echo -e "  ${RED}✗ Missing test file${NC}"
    ALL_PASSED=false
fi
echo ""

# Test 7: Check examples
echo -e "${YELLOW}[7/7] Checking examples...${NC}"
if [ -f "examples/visualization_demo.py" ]; then
    echo "  ✓ examples/visualization_demo.py"
else
    echo -e "  ${RED}✗ Missing example file${NC}"
    ALL_PASSED=false
fi
echo ""

# Summary
echo "=================================================="
if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Install dependencies: pip install fastapi websockets"
    echo "  2. Run tests: pytest tests/test_visualization_server.py -v"
    echo "  3. Try the demo: python examples/visualization_demo.py"
    echo "  4. Start the server: uacs serve --with-ui"
    echo ""
    echo "Documentation: docs/VISUALIZATION.md"
    exit 0
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo ""
    echo "Please review the errors above and ensure all files are in place."
    exit 1
fi
