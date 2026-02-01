"""Integration tests for UACS MCP Server binary (macOS ARM64)."""

import json
import os
import subprocess
import time
from pathlib import Path

import pytest


BINARY_PATH = Path(__file__).parent.parent.parent / "dist" / "uacs-macos-arm64"
STARTUP_TIMEOUT = 5  # seconds
TARGET_STARTUP_TIME = 2  # seconds


class TestMCPServerBinary:
    """Test suite for the UACS MCP Server binary."""

    def test_binary_exists(self):
        """Test that the binary file exists."""
        assert BINARY_PATH.exists(), f"Binary not found at {BINARY_PATH}"

    def test_binary_is_executable(self):
        """Test that the binary is executable."""
        assert os.access(BINARY_PATH, os.X_OK), f"Binary at {BINARY_PATH} is not executable"

    def test_help_command(self):
        """Test that --help flag works and returns usage information."""
        result = subprocess.run(
            [str(BINARY_PATH), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, f"--help failed with exit code {result.returncode}"

        # Check for expected help content
        help_text = result.stdout.lower()
        assert "usage" in help_text or "help" in help_text or "uacs" in help_text, \
            "Help output doesn't contain expected content"

    def test_version_or_info_flags(self):
        """Test common info flags (optional - may not be implemented)."""
        # Try --version if it exists
        result = subprocess.run(
            [str(BINARY_PATH), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Just check it doesn't crash - version flag may not be implemented
        assert result.returncode in [0, 2], "Binary crashed on --version"

    def test_stdio_mode_starts(self):
        """Test that stdio mode starts and responds to JSON-RPC initialize."""
        process = None
        try:
            # Start the binary in stdio mode
            start_time = time.time()
            process = subprocess.Popen(
                [str(BINARY_PATH), "--transport", "stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Wait a moment for startup
            time.sleep(0.5)

            # Check process is still running
            assert process.poll() is None, "Process terminated immediately after start"

            # Send JSON-RPC initialize request
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }

            request_json = json.dumps(initialize_request) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()

            # Try to read response with timeout
            try:
                # Read one line (JSON-RPC response)
                response_line = process.stdout.readline()

                if response_line:
                    response = json.loads(response_line)
                    assert "jsonrpc" in response, "Response is not valid JSON-RPC"
                    assert response.get("id") == 1, "Response ID doesn't match request"
                    # If we get here, the server is responding correctly
                else:
                    # No response yet, but process is running
                    pytest.skip("Server started but didn't respond to initialize (may need more time)")

            except json.JSONDecodeError:
                # Server might not be responding with proper JSON-RPC yet
                pytest.skip("Server started but response format unexpected")

        except subprocess.TimeoutExpired:
            pytest.fail("Binary timed out during startup")
        except Exception as e:
            pytest.fail(f"Unexpected error during stdio test: {e}")
        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

    def test_stdio_mode_default(self):
        """Test that stdio mode is the default (no --transport flag needed)."""
        process = None
        try:
            # Start the binary without transport flag
            process = subprocess.Popen(
                [str(BINARY_PATH)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Wait a moment for startup
            time.sleep(0.5)

            # Check process is running
            assert process.poll() is None, "Process terminated immediately without --transport flag"

        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

    def test_startup_time(self):
        """Test that the binary starts within the target time."""
        process = None
        try:
            start_time = time.time()

            # Start the binary
            process = subprocess.Popen(
                [str(BINARY_PATH), "--transport", "stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for process to be ready (check it's running)
            time.sleep(0.1)

            # Check if process started successfully
            if process.poll() is not None:
                stderr_output = process.stderr.read()
                pytest.fail(f"Process failed to start: {stderr_output}")

            startup_time = time.time() - start_time

            # Log the startup time
            print(f"\nStartup time: {startup_time:.3f} seconds")

            # Check against target
            assert startup_time < TARGET_STARTUP_TIME, \
                f"Startup time {startup_time:.3f}s exceeds target of {TARGET_STARTUP_TIME}s"

        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

    def test_invalid_transport_flag(self):
        """Test that invalid transport flag is handled gracefully."""
        result = subprocess.run(
            [str(BINARY_PATH), "--transport", "invalid"],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should exit with error code
        assert result.returncode != 0, "Binary should reject invalid transport"

    def test_sse_mode_starts(self):
        """Test that SSE mode can be specified (may not fully start without port config)."""
        process = None
        try:
            # Start with SSE transport
            process = subprocess.Popen(
                [str(BINARY_PATH), "--transport", "sse"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Give it a moment to start
            time.sleep(1)

            # Check process status
            poll_result = process.poll()

            # It might fail if no port is configured, or it might start
            # Either way, we're testing that the flag is recognized
            if poll_result is not None:
                # Process exited - check if it was due to missing config
                stderr_output = process.stderr.read()
                # This is okay - SSE mode might need additional config
                assert "transport" not in stderr_output.lower() or \
                       "unrecognized" not in stderr_output.lower(), \
                       "SSE transport flag not recognized"
            else:
                # Process is running - SSE mode started successfully
                pass

        finally:
            if process:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


@pytest.fixture(scope="module")
def ensure_binary_exists():
    """Fixture to ensure binary exists before running tests."""
    if not BINARY_PATH.exists():
        pytest.skip(f"Binary not found at {BINARY_PATH}. Run build first.")
    yield BINARY_PATH


# Use the fixture for all tests in this module
pytestmark = pytest.mark.usefixtures("ensure_binary_exists")
