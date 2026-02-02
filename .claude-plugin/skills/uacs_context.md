# UACS Context Management

You have access to **UACS (Universal Agent Context System)** for perfect conversation recall across sessions.

## What UACS Does

Every conversation you have with me is **automatically stored** with:
- ✅ **100% fidelity** - Exact storage, no summarization loss
- ✅ **Automatic deduplication** - 15% token savings
- ✅ **Topic tagging** - Organized by security, performance, testing, etc.
- ✅ **Perfect recall** - Retrieve any past discussion

## When to Use UACS

### Retrieve Past Conversations
- User: "What did we discuss about security?"
- User: "Remind me about that SQL injection fix"
- User: "What performance issues did we find?"

### Multi-Session Projects
- Day 1: Review code for security
- Day 2: Continue from exact context (no loss!)
- Week later: Recall specific findings

### Focus on Topics
- Filter by: security, performance, bug, feature, refactor, etc.
- Get only relevant context (not everything)

## How to Retrieve Context

If the UACS MCP server is running, you can use:

```
@uacs_search_context query="security issues" topics=["security"]
```

Or simply ask naturally:
- "Can you check UACS for what we discussed about X?"
- "Retrieve our previous conversation about Y"
- "What did we decide about Z?"

## What Gets Stored

**Everything:**
- All your messages
- All my responses
- Tool uses
- Code snippets
- Decisions made
- Issues found

**Organized by:**
- Topics (security, performance, testing, etc.)
- Session ID
- Timestamp
- Turn count

## Benefits

1. **Never Lose Context**: Sessions never truly end - everything is saved
2. **Perfect Continuity**: Pick up exactly where you left off
3. **Time Savings**: No re-explaining projects after context resets
4. **Focused Retrieval**: Get only what you need by topic
5. **Zero Effort**: Automatic storage, no manual work

## Technical Details

- **Storage**: `.state/context/` in your project
- **Format**: JSON with compression
- **Deduplication**: Automatic (15% savings)
- **Fidelity**: 100% exact (no summarization)
- **Privacy**: Local-only, never leaves your machine

## Example Session

```
Session 1 (Day 1):
User: Review authentication.py for security
Claude: Found SQL injection at line 42, timing attack at line 78...
[Stored automatically with topics: security, authentication]

Session 2 (Day 2):
User: What was that SQL injection issue?
Claude: [Retrieves from UACS] At line 42 in auth.py, using string
        concatenation for SQL queries. Recommended parameterized queries.
User: Thanks! Now let's fix it.
```

## Troubleshooting

**Q: How do I know it's working?**
A: Check `.state/context/` directory - you'll see JSON files for each session.

**Q: Can I disable automatic storage?**
A: Yes, remove the SessionEnd hook from `.claude-plugin/plugin.json`

**Q: How much does storage cost?**
A: Zero. Storage is local, no cloud fees. Compression saves tokens on retrieval.

**Q: What if UACS fails?**
A: Hook degrades gracefully - never blocks Claude Code. Check errors in terminal.

---

**UACS makes every conversation permanent and perfectly recalled. Use it to build continuous context across all your development sessions.**
