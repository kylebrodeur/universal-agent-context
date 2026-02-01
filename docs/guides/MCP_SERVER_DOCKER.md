# UACS MCP Server: Docker Installation

Run UACS in a containerized environment. Ideal for servers and teams.

## Prerequisites

- Docker installed and running
- Docker Compose (optional but recommended)

## Quick Start

Run directly:
```bash
docker run -p 3000:3000 universal-agent-context serve
```

> **Note:** The `universal-agent-context` image must be built locally first. See [Building Locally](#building-locally) below.

## Docker Compose

Create a `docker-compose.yml`:

```yaml
services:
  uacs:
    image: universal-agent-context:latest
    ports:
      - "3000:3000"
    volumes:
      - ./my-project:/app/project
    environment:
      - UACS_PROJECT_PATH=/app/project
```

## Configuration

### Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `UACS_PROJECT_PATH` | Path to the project root inside the container | `/app` |
| `UACS_LOG_LEVEL` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `UACS_HOST` | Host to bind the server to | `0.0.0.0` |
| `UACS_PORT` | Port to bind the server to | `3000` |

### Volume Mounting

To persist data and allow UACS to access your project files, mount your local project directory to the container.

```bash
docker run -v $(pwd):/app/project -p 3000:3000 universal-agent-context serve
```

### Building Locally

If you want to build the image from source:

```bash
git clone https://github.com/kylebrodeur/universal-agent-context
cd universal-agent-context
docker build -t universal-agent-context .
```
