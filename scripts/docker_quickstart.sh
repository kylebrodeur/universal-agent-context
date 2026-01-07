#!/bin/bash
# UACS MCP Server - Docker Quick Start
# Builds and runs the UACS MCP server in Docker

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CONTAINER_NAME="uacs-mcp"
IMAGE_NAME="uacs:latest"
PORT=${UACS_PORT:-3000}

echo "🐳 UACS MCP Server - Docker Quick Start"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗${NC} Docker is not installed."
    echo ""
    echo "Please install Docker first:"
    echo "  macOS: https://docs.docker.com/desktop/install/mac-install/"
    echo "  Linux: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}✗${NC} Docker is not running."
    echo "Please start Docker and try again."
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is installed and running"
echo ""

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}⚠${NC}  Container '$CONTAINER_NAME' already exists."
    read -p "Do you want to remove it and start fresh? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping and removing existing container..."
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Container removed"
    else
        echo "Exiting. To start the existing container, run:"
        echo "  docker start $CONTAINER_NAME"
        exit 0
    fi
    echo ""
fi

# Check if image exists
if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE_NAME}$"; then
    echo -e "${GREEN}✓${NC} Docker image '$IMAGE_NAME' exists"
    read -p "Rebuild image? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        BUILD_IMAGE=true
    else
        BUILD_IMAGE=false
    fi
else
    echo "Docker image '$IMAGE_NAME' not found."
    BUILD_IMAGE=true
fi

# Build image if needed
if [ "$BUILD_IMAGE" = true ]; then
    echo ""
    echo "Building Docker image..."
    echo "------------------------"
    if docker build -f Dockerfile.mcp-server -t "$IMAGE_NAME" .; then
        echo -e "${GREEN}✓${NC} Image built successfully"

        # Show image size
        SIZE=$(docker images --format "{{.Size}}" "$IMAGE_NAME")
        echo -e "${BLUE}ℹ${NC}  Image size: $SIZE"
    else
        echo -e "${RED}✗${NC} Failed to build Docker image"
        exit 1
    fi
fi

# Start container
echo ""
echo "Starting container..."
echo "---------------------"
echo "Container name: $CONTAINER_NAME"
echo "Port: $PORT"
echo ""

if docker run -d \
    --name "$CONTAINER_NAME" \
    -p "${PORT}:3000" \
    -e UACS_TRANSPORT=sse \
    "$IMAGE_NAME"; then
    echo -e "${GREEN}✓${NC} Container started successfully"
else
    echo -e "${RED}✗${NC} Failed to start container"
    exit 1
fi

# Wait for container to be healthy
echo ""
echo "Waiting for server to be ready..."
sleep 3

# Check health
HEALTH_URL="http://localhost:${PORT}/health"
if curl -s "$HEALTH_URL" | grep -q "ok"; then
    echo -e "${GREEN}✓${NC} Server is healthy!"
else
    echo -e "${YELLOW}⚠${NC}  Health check failed, but container may still be starting."
    echo "Run 'docker logs $CONTAINER_NAME' to check status."
fi

# Show status
echo ""
echo "========================================"
echo -e "${GREEN}Docker container is running!${NC}"
echo ""
echo "Container: $CONTAINER_NAME"
echo "Health endpoint: $HEALTH_URL"
echo ""
echo "Useful commands:"
echo "  View logs:    docker logs $CONTAINER_NAME"
echo "  Follow logs:  docker logs -f $CONTAINER_NAME"
echo "  Stop:         docker stop $CONTAINER_NAME"
echo "  Start:        docker start $CONTAINER_NAME"
echo "  Remove:       docker rm -f $CONTAINER_NAME"
echo ""
echo "To configure Claude Desktop, add to your config:"
echo '  "uacs": {'
echo '    "url": "http://localhost:'$PORT'/sse"'
echo '  }'
echo ""
