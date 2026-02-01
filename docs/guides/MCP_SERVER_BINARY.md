# UACS MCP Server: Binary Installation

Run the Universal Agent Context System (UACS) MCP server as a standalone binary without installing Python.

## Supported Platforms

- **macOS**: Apple Silicon (arm64) and Intel (x86_64)
- **Linux**: x86_64 (glibc 2.17+)
- **Windows**: x86_64 (Windows 10+)

## Installation

### Option 1: Automated Install (Recommended)

Coming soon.

### Option 2: Manual Download

1. Download the binary for your platform from the [Releases page](https://github.com/kylebrodeur/universal-agent-context/releases).
2. Make it executable (macOS/Linux):
   ```bash
   chmod +x uacs-macos-arm64
   mv uacs-macos-arm64 uacs
   ```
3. Move to your PATH (optional).

## Usage

Start the server:
```bash
./uacs serve
```

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "uacs": {
      "command": "/absolute/path/to/uacs",
      "args": ["serve"]
    }
  }
}
```

## Troubleshooting

### macOS: "Developer cannot be verified"

If macOS prevents the binary from running:
1. Open **System Settings** > **Privacy & Security**.
2. Scroll down to the security section.
3. Click **Allow Anyway** next to the blocked application message.
4. Run the command again.

Alternatively, remove the quarantine attribute via terminal:
```bash
xattr -d com.apple.quarantine uacs
```

### Permission Denied

Ensure the binary has executable permissions:
```bash
chmod +x uacs
```

### "Command not found"

If you moved the binary to a folder in your PATH but it's not found, try restarting your terminal or checking your PATH configuration:
```bash
echo $PATH
```
