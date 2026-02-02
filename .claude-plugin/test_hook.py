#!/usr/bin/env python3
"""Test script for UACS Claude Code hook.

This script creates a mock Claude Code transcript and tests
that the hook properly stores it in UACS.
"""

import json
import subprocess
import tempfile
from pathlib import Path


def create_mock_transcript() -> Path:
    """Create a mock Claude Code transcript (JSONL format)."""
    transcript = [
        {
            "role": "user",
            "content": "Please review authentication.py for security vulnerabilities",
        },
        {
            "role": "assistant",
            "content": "I found SQL injection at line 42 and timing attack at line 78",
        },
        {
            "role": "user",
            "content": "What was the SQL injection issue again?",
        },
        {
            "role": "assistant",
            "content": "At line 42, using string concatenation for SQL queries",
        },
    ]

    # Write to temp file
    temp_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False
    )
    for turn in transcript:
        temp_file.write(json.dumps(turn) + "\n")
    temp_file.close()

    return Path(temp_file.name)


def test_hook():
    """Test the UACS hook with mock data."""
    print("🧪 Testing UACS Claude Code Hook")
    print("=" * 60)

    # Create mock transcript
    print("\n1. Creating mock transcript...")
    transcript_path = create_mock_transcript()
    print(f"   ✓ Created: {transcript_path}")

    # Create hook input
    hook_input = {
        "transcript_path": str(transcript_path),
        "session_id": "test-session-123",
        "project_dir": ".",
        "timestamp": "2026-02-01T10:00:00Z",
    }

    print("\n2. Running hook...")
    print(f"   Session ID: {hook_input['session_id']}")

    # Run hook
    try:
        result = subprocess.run(
            ["python3", ".claude-plugin/hooks/uacs_store.py"],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            timeout=10,
        )

        print(f"   Return code: {result.returncode}")

        # Parse output
        if result.stdout:
            output = json.loads(result.stdout)
            print("\n3. Hook output:")
            print(json.dumps(output, indent=2))

            # Check success
            if output.get("continue") and "message" in output:
                print("\n✅ SUCCESS: Hook stored session to UACS")
                print(f"   Message: {output['message']}")

                # Check if file was created
                state_dir = Path(".state/context")
                if state_dir.exists():
                    context_files = list(state_dir.glob("*.json"))
                    print(f"\n4. Verification:")
                    print(f"   ✓ Context directory exists: {state_dir}")
                    print(f"   ✓ Files created: {len(context_files)}")
                    if context_files:
                        print(f"   ✓ Latest: {context_files[-1].name}")
                else:
                    print(f"\n⚠  Warning: .state/context/ not found")

            elif "error" in output:
                print(f"\n⚠  Warning: {output['error']}")
                print(f"   Message: {output.get('message', 'N/A')}")
            else:
                print("\n❌ FAILED: Unexpected output")

        else:
            print(f"\n❌ FAILED: No stdout")
            if result.stderr:
                print(f"   stderr: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("\n❌ FAILED: Hook timed out (>10s)")
    except json.JSONDecodeError as e:
        print(f"\n❌ FAILED: Invalid JSON output")
        print(f"   Error: {e}")
        print(f"   stdout: {result.stdout}")
    except Exception as e:
        print(f"\n❌ FAILED: {type(e).__name__}: {e}")
    finally:
        # Cleanup
        transcript_path.unlink()
        print(f"\n5. Cleaned up temp file: {transcript_path}")

    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    test_hook()
