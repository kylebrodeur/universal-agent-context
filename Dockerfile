FROM ghcr.io/astral-sh/uv:python3.11-alpine

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache libstdc++

# Copy project files
COPY pyproject.toml README.md ./
COPY src ./src

# Install dependencies using uv (much faster than pip)
RUN uv pip install --system --no-cache .

# Create a non-root user
RUN adduser -D uacs
USER uacs

# Expose port
EXPOSE 3000

# Set running mode to SSE by default
ENV UACS_TRANSPORT=sse

# Entrypoint
ENTRYPOINT ["python", "-m", "uacs.mcp_server_entry"]
