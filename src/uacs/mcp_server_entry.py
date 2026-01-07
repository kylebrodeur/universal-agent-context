"""Entry point for UACS MCP Server."""
import argparse
import asyncio
import sys
import os


async def run_sse(port: int = 3000):
    """Run the server using SSE transport."""
    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse, Response
    from starlette.routing import Route, Mount
    from mcp.server.sse import SseServerTransport
    from uacs.protocols.mcp.skills_server import server

    # Initialize SSE transport
    # Note: '/messages/' must be a relative path for the client to post to.
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        """Handle SSE connection."""
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )
        return Response()

    async def health_check(request):
        """Health check endpoint."""
        return JSONResponse({"status": "ok"})

    routes = [
        Route("/sse", endpoint=handle_sse),
        Mount("/messages", app=sse.handle_post_message),
        Route("/health", endpoint=health_check),
    ]

    app = Starlette(routes=routes)
    
    # Configure uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()

async def run_stdio():
    """Run the server using stdio transport."""
    from uacs.protocols.mcp.skills_server import server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )

def main():
    parser = argparse.ArgumentParser(description="UACS MCP Server")
    default_transport = os.environ.get("UACS_TRANSPORT", "stdio")
    parser.add_argument("--transport", choices=["stdio", "sse"], default=default_transport, help="Transport mode")
    parser.add_argument("--port", type=int, default=3000, help="Port for SSE server")
    
    # Parse args (this will handle --help and exit automatically)
    args = parser.parse_args()
    
    # If we get here, args are valid
    try:
        if args.transport == "sse":
            asyncio.run(run_sse(args.port))
        else:
            asyncio.run(run_stdio())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()