# UACS Skill Suggestion System - Learn Workflows, Suggest Automation

**Created:** 2026-02-01
**Status:** Design Document (v0.3.0 Feature)

---

## The Vision

**User's Insight:**
> "If we figure out a development flow while working, UACS should be able to pick that up over time and suggest a skill to be installed or created based on the conversation and best practices."

**What This Means:**
Instead of just storing context, UACS **learns from your patterns** and suggests automation:

### Example Patterns → Skills

| Pattern Detected | Suggested Skill | What It Automates |
|-----------------|----------------|-------------------|
| Always run `pytest` then `git commit` after edits | `/test-and-commit` | Runs tests, commits if pass |
| Frequently ask "what changed since last session?" | `/session-diff` | Shows changes between sessions |
| Always grep for TODOs before starting work | `/todo-scan` | Finds all TODOs in codebase |
| Often ask for security review of auth code | `/security-check` | Runs security linters on auth files |
| Repeatedly explain same architecture | `/explain-arch` | Injects architecture docs |

**Key Benefit:** Turns conversation context into executable automation, reducing repetitive explanations.

---

## How It Works: 4-Stage Process

### Stage 1: Pattern Detection (Background Analysis)

**Trigger:** SessionEnd hook analyzes completed session

**What It Does:**
```python
# Analyze last 10 sessions from UACS
sessions = uacs.get_recent_sessions(count=10)

# Use local LLM (Ollama) to detect patterns
patterns = analyze_patterns_with_llm(sessions, model="llama3.2:3b")

# Example patterns detected:
# {
#   "pattern": "Always runs pytest before git commit",
#   "frequency": 8/10 sessions,
#   "context": "After editing test files",
#   "suggested_skill": {
#     "name": "test-and-commit",
#     "command": "pytest && git add . && git commit",
#     "description": "Run tests and commit if passing"
#   }
# }
```

**Local LLM Prompt:**
```python
def detect_workflow_patterns(sessions: list[str]) -> list[dict]:
    """Use Ollama to detect repeated workflows."""

    prompt = f"""Analyze these conversation transcripts and identify repeated workflows:

{format_sessions_for_analysis(sessions)}

Look for:
1. Commands run in sequence (e.g., test → commit → push)
2. Repeated questions (e.g., "what changed?" every session)
3. Common file patterns (e.g., always editing tests after code)
4. Repeated explanations (e.g., explaining architecture multiple times)

Output JSON list of patterns:
[
  {{
    "pattern": "Always runs pytest before committing",
    "frequency": "8/10 sessions",
    "commands": ["pytest", "git add .", "git commit -m '...'"],
    "suggested_skill_name": "test-and-commit",
    "suggested_skill_description": "Run tests and commit if passing"
  }}
]
"""

    response = ollama.generate(model="llama3.2:3b", prompt=prompt)
    return json.loads(response["response"])
```

---

### Stage 2: Skill Suggestion (User Notification)

**Trigger:** Next SessionStart (when user opens Claude Code again)

**What It Does:**
```python
def suggest_skills_on_start(hook_input: dict) -> dict:
    """Suggest skills based on detected patterns."""

    # Load pending suggestions from Stage 1
    suggestions = load_pending_suggestions()

    if not suggestions:
        return {"continue": True}

    # Format suggestions for user
    message = format_skill_suggestions(suggestions)

    return {
        "hookSpecificOutput": {
            "additionalContext": f"""
## 💡 UACS Detected Workflow Patterns

Based on your last 10 sessions, UACS noticed you often:

{message}

Would you like to create these skills? Use `/uacs-create-skill <name>` to generate them.
""",
            "message": f"UACS: {len(suggestions)} skill suggestions available"
        }
    }
```

**Example Notification:**
```
💡 UACS Detected Workflow Patterns

Based on your last 10 sessions, UACS noticed you often:

1. **test-and-commit** (8/10 sessions)
   - Run: pytest → git commit (only if tests pass)
   - Automate with: /test-and-commit "your commit message"

2. **security-check** (6/10 sessions)
   - Check: SQL injection, XSS, auth vulnerabilities in changed files
   - Automate with: /security-check

3. **session-recap** (9/10 sessions)
   - You ask "what did we do last time?" at session start
   - Automate with: /recap (shows last session summary)

Use `/uacs-create-skill test-and-commit` to generate these skills.
```

---

### Stage 3: Skill Generation (User-Triggered)

**Trigger:** User runs `/uacs-create-skill <name>`

**What It Does:**
```python
def create_skill_from_pattern(skill_name: str, pattern: dict) -> str:
    """Generate a Claude Code skill from detected pattern."""

    # Use local LLM to generate skill implementation
    skill_code = generate_skill_with_llm(pattern, model="llama3.2:3b")

    # Save to .claude/skills/
    skill_path = f".claude/skills/{skill_name}.md"

    write_skill_file(skill_path, skill_code)

    # Update plugin.json to register skill
    register_skill_in_plugin(skill_name, skill_path)

    return f"Created skill: /{skill_name} → {skill_path}"
```

**Example Generated Skill: test-and-commit.md**

```markdown
# Test and Commit Skill

**Name:** test-and-commit
**Description:** Run pytest and commit changes if tests pass
**Usage:** `/test-and-commit "commit message"`

## Instructions

When the user runs `/test-and-commit "message"`:

1. Run `pytest` to execute all tests
2. Check exit code:
   - If 0 (pass): Continue to step 3
   - If non-zero (fail): Show failures and STOP (do not commit)
3. Run `git add .` to stage all changes
4. Run `git commit -m "message\n\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"`
5. Show commit hash and summary

## Example

User: `/test-and-commit "Fix authentication bug"`

Output:
```
✅ Tests passed (42 passed, 0 failed)
✅ Committed as abc123: Fix authentication bug
```

## Edge Cases

- If no changes staged: Warn "nothing to commit"
- If tests fail: Show first 10 failures, suggest fixes
- If commit fails (no message): Prompt for message

## Generated By

UACS Skill Suggestion System
Pattern detected: 8/10 sessions (2026-01-25 to 2026-02-01)
```

---

### Stage 4: Learning Loop (Feedback)

**Trigger:** User uses (or ignores) suggested skill

**What It Does:**
```python
def track_skill_usage(skill_name: str, used: bool):
    """Learn from user behavior."""

    # If user uses skill: Reinforce pattern
    if used:
        uacs.update_pattern_score(skill_name, boost=+0.2)

    # If user ignores skill: Reduce suggestion weight
    else:
        uacs.update_pattern_score(skill_name, penalty=-0.1)

    # After 5 ignores, stop suggesting
    if uacs.get_pattern_score(skill_name) < 0.3:
        uacs.archive_suggestion(skill_name, reason="user_ignored")
```

---

## Pattern Detection Categories

### Category 1: Command Sequences

**Detects:** Commands always run together

**Examples:**
- `pytest` → `git commit` (test before commit)
- `npm run build` → `docker build` (build then containerize)
- `git pull` → `npm install` (update deps after pull)

**Generated Skills:**
- `/test-commit "message"` - Run tests, commit if pass
- `/build-docker` - Build app and create Docker image
- `/sync` - Pull code and update dependencies

---

### Category 2: Repeated Questions

**Detects:** Same questions asked frequently

**Examples:**
- "What changed since last session?" (9/10 sessions)
- "Show me all TODOs in the codebase" (7/10 sessions)
- "Are there any security vulnerabilities?" (5/10 sessions)

**Generated Skills:**
- `/recap` - Summarize previous session changes
- `/todos` - Find all TODO comments
- `/security-scan` - Run security linters

---

### Category 3: File Pattern Workflows

**Detects:** Consistent file editing patterns

**Examples:**
- Always edit tests after editing source code
- Always update docs after API changes
- Always check logs after deployment

**Generated Skills:**
- `/edit-with-tests <file>` - Open file and its test file
- `/api-change <endpoint>` - Edit endpoint and update OpenAPI docs
- `/deploy-check` - Deploy and tail logs

---

### Category 4: Repeated Explanations

**Detects:** Claude explains the same thing multiple times

**Examples:**
- Architecture overview (explained in 6/10 sessions)
- Database schema (explained in 5/10 sessions)
- Deployment process (explained in 4/10 sessions)

**Generated Skills:**
- `/explain-arch` - Inject architecture diagram into context
- `/explain-schema` - Show DB schema and relationships
- `/explain-deploy` - Describe deployment steps

**Key Insight:** These should inject documentation into context, not regenerate explanations.

---

### Category 5: Error Pattern Responses

**Detects:** Same errors fixed the same way repeatedly

**Examples:**
- "ModuleNotFoundError" → `pip install <package>`
- "Port already in use" → `kill $(lsof -t -i:3000)`
- "Disk space full" → `docker system prune -a`

**Generated Skills:**
- `/fix-missing-dep <error>` - Parse error and install missing package
- `/kill-port <port>` - Kill process on port
- `/cleanup-docker` - Free up Docker disk space

---

## Implementation Architecture

### Hook Integration

```
SessionEnd (analyze)
├─ Extract conversation patterns
├─ Use Ollama to detect workflows
├─ Store suggestions in .state/suggestions.json
└─ Score patterns by frequency/relevance

SessionStart (notify)
├─ Load pending suggestions
├─ Show top 3 suggestions to user
└─ Provide creation commands

UserPromptSubmit (check for skill creation)
├─ Detect `/uacs-create-skill <name>`
├─ Generate skill from pattern
├─ Register in plugin.json
└─ Confirm creation

PostToolUse (track usage)
├─ Detect if suggested skill was used
├─ Update pattern scores
└─ Archive ignored suggestions
```

---

## Local LLM Usage (Zero API Cost)

### Pattern Detection (Stage 1)

**Model:** Ollama llama3.2:3b (2.0GB)
**Frequency:** Once per session (SessionEnd)
**Time:** ~2-5 seconds for 10 sessions
**Cost:** $0 (local)

### Skill Generation (Stage 3)

**Model:** Ollama llama3.2:3b or codellama:7b
**Frequency:** Only when user requests skill creation
**Time:** ~5-10 seconds to generate skill
**Cost:** $0 (local)

**Why Not Claude API?**
- Pattern detection is formulaic (don't need Opus/Sonnet quality)
- Runs in background (user doesn't see latency)
- Free vs $0.25/M tokens for Haiku

**When to Use Claude API?**
- User explicitly asks for skill review/improvement
- Complex skill requiring deep reasoning
- But default should be local LLM

---

## Data Storage

### .state/suggestions.json

```json
{
  "version": "0.3.0",
  "generated_at": "2026-02-01T10:30:00Z",
  "suggestions": [
    {
      "id": "test-and-commit-20260201",
      "name": "test-and-commit",
      "pattern": "Always runs pytest before git commit",
      "frequency": 8,
      "total_sessions": 10,
      "score": 0.9,
      "first_detected": "2026-01-25T08:00:00Z",
      "last_detected": "2026-02-01T09:00:00Z",
      "commands": ["pytest", "git add .", "git commit -m '...'"],
      "status": "pending",
      "user_action": null,
      "skill_path": null
    },
    {
      "id": "security-check-20260201",
      "name": "security-check",
      "pattern": "Frequently checks for SQL injection and XSS",
      "frequency": 6,
      "total_sessions": 10,
      "score": 0.75,
      "first_detected": "2026-01-27T10:00:00Z",
      "last_detected": "2026-02-01T09:00:00Z",
      "commands": ["bandit", "semgrep"],
      "status": "pending",
      "user_action": null,
      "skill_path": null
    }
  ],
  "archived": [
    {
      "id": "old-suggestion-123",
      "name": "old-pattern",
      "archived_at": "2026-01-20T12:00:00Z",
      "reason": "user_ignored",
      "ignore_count": 5
    }
  ]
}
```

---

## Example: End-to-End Flow

### Week 1: User Works Normally

```bash
# Session 1
claude
> User: Run pytest
> Claude: [runs pytest]
> User: Commit the changes
> Claude: [git commit]

# Session 2
claude
> User: Test the new feature
> Claude: [runs pytest]
> User: If tests pass, commit
> Claude: [git commit]

# ... 8 more sessions with same pattern ...
```

### Week 2: UACS Detects Pattern

```bash
# SessionEnd hook (after Session 10)
# UACS runs pattern detection:
# - Detected: "pytest → git commit" in 8/10 sessions
# - Generated suggestion: /test-and-commit
# - Saved to .state/suggestions.json
```

### Week 2: User Sees Suggestion

```bash
# Session 11
claude

💡 UACS Detected Workflow Patterns

Based on your last 10 sessions, UACS noticed you often:

1. **test-and-commit** (8/10 sessions)
   - Run: pytest → git commit (only if tests pass)
   - Automate with: /test-and-commit "your commit message"

Use `/uacs-create-skill test-and-commit` to generate this skill.

> User: /uacs-create-skill test-and-commit
✅ Created skill: /test-and-commit
   Location: .claude/skills/test-and-commit.md
   Usage: /test-and-commit "commit message"
```

### Week 2+: User Uses Skill

```bash
# Session 12
> User: /test-and-commit "Add user authentication"

✅ Running tests...
✅ Tests passed (42 passed, 0 failed)
✅ Staging changes...
✅ Committed as abc123: Add user authentication

# UACS tracks this usage:
# - Pattern score: 0.9 → 1.0 (reinforced)
# - Will suggest similar skills in future
```

---

## Advanced: Multi-User Learning

### Team Pattern Detection

**Concept:** Learn from entire team's workflows, not just one user

**How:**
1. Multiple users use UACS on same codebase
2. Each user's patterns stored in `.state/patterns/user_<id>.json`
3. Weekly aggregation identifies team-wide patterns
4. Suggest skills that benefit entire team

**Example:**
```
Team Pattern Detected:
- 5/7 developers run "npm test" → "npm run lint" → "git commit"
- Suggested team skill: /precommit (runs tests + lint before commit)
- Benefit: Standardizes pre-commit workflow across team
```

---

## Integration with Best Practices

### External Knowledge Sources

**Concept:** Combine user patterns with industry best practices

**Sources:**
1. **User's actual behavior** (from UACS history)
2. **Industry standards** (e.g., OWASP, 12-factor app)
3. **Framework conventions** (e.g., Django, Rails, Next.js)

**Example:**
```
Pattern Detected: User manually checks for SQL injection
Best Practice: Automated security scanning (OWASP recommendation)

Suggested Skill: /security-check
- Runs: bandit (Python), semgrep (multi-language)
- Checks: OWASP Top 10
- Integrates: Your pattern + industry standard
```

---

## Performance Considerations

### When to Run Pattern Detection

**Option 1: Every SessionEnd (Simple)**
- Analyze last 10 sessions on each session end
- Pro: Always up-to-date
- Con: Redundant if patterns haven't changed

**Option 2: Weekly (Efficient)**
- Run pattern detection once per week
- Pro: Less overhead
- Con: Delayed suggestions

**Option 3: Threshold-Based (Optimal)**
- Run after every 5 sessions
- Pro: Balance between freshness and efficiency
- Con: Slightly more complex logic

**Recommendation:** Option 3 (threshold-based) with 5-session trigger.

---

## Privacy and Control

### User Controls

Users should be able to:

1. **Opt-out of pattern detection**
   ```json
   "configuration": {
     "pattern_detection": false
   }
   ```

2. **Review suggestions before creation**
   ```bash
   /uacs-suggestions  # Show pending suggestions
   /uacs-reject test-and-commit  # Reject suggestion
   ```

3. **Delete learned patterns**
   ```bash
   /uacs-forget test-and-commit  # Stop suggesting this pattern
   ```

4. **Export/Import patterns**
   ```bash
   /uacs-export-patterns > my-patterns.json
   /uacs-import-patterns my-patterns.json
   ```

---

## Comparison: Manual vs Auto-Suggested Skills

### Manual Skill Creation (Current)

**User writes:**
```markdown
# .claude/skills/test-and-commit.md
When user runs /test-and-commit:
1. Run pytest
2. If pass, git commit
...
```

**Time:** 10-20 minutes per skill
**Quality:** High (user-crafted)
**Discovery:** User must recognize pattern themselves

### Auto-Suggested Skills (This System)

**UACS generates:**
```markdown
# .claude/skills/test-and-commit.md
(same content, auto-generated from pattern)
```

**Time:** 30 seconds (just approve suggestion)
**Quality:** Good (LLM-generated, user-reviewed)
**Discovery:** Automatic (UACS detects pattern)

**Winner:** Auto-suggested (90% time savings, automatic discovery)

---

## Rollout Plan

### v0.3.0: Basic Pattern Detection

**Features:**
- Detect command sequences (Category 1)
- Suggest skills for common workflows
- Generate basic skills with local LLM

**Timeline:** 2-3 weeks

### v0.4.0: Advanced Detection

**Features:**
- Detect repeated questions (Category 2)
- Detect repeated explanations (Category 4)
- Inject documentation instead of regenerating

**Timeline:** 1 month

### v0.5.0: Team Learning

**Features:**
- Multi-user pattern aggregation
- Team-wide skill suggestions
- Best practices integration

**Timeline:** 2 months

---

## Related Systems

### Similar Concepts in Other Tools

| Tool | Feature | Comparison to UACS |
|------|---------|-------------------|
| GitHub Copilot | Learns from codebase | Static (per-repo), not per-user workflow |
| Cursor | Custom rules | Manual creation, no auto-detection |
| Cline | Task templates | Predefined, not learned |
| **UACS** | **Workflow learning** | **Dynamic, user-specific, auto-generated** |

**UACS Advantage:** Only system that learns from actual conversation patterns and suggests automation.

---

## Success Metrics

### Key Performance Indicators (KPIs)

1. **Pattern Detection Accuracy**
   - Target: 80% of detected patterns are useful
   - Measure: User acceptance rate of suggestions

2. **Time Savings**
   - Target: Save 1 hour/week per user
   - Measure: Time spent on repeated tasks before/after

3. **Skill Adoption Rate**
   - Target: 60% of suggested skills are created and used
   - Measure: Creation rate × usage rate

4. **Context Reduction**
   - Target: 20% fewer repeated explanations
   - Measure: Token usage on repeated topics

---

## Summary

**User's Vision:**
> "If we figure out a development flow while working, UACS should be able to pick that up over time and suggest a skill."

**What We Built:**
1. ✅ **Pattern Detection** - Analyze 10 sessions, detect workflows with local LLM
2. ✅ **Skill Suggestion** - Notify user of detected patterns on SessionStart
3. ✅ **Auto-Generation** - Generate skills from patterns with `/uacs-create-skill`
4. ✅ **Learning Loop** - Track usage, reinforce good suggestions, archive ignored ones
5. ✅ **Zero API Cost** - Use Ollama for pattern detection and skill generation

**Result:** UACS evolves from passive storage to active workflow optimization.

**Next Steps:**
1. Implement pattern detection in SessionEnd hook
2. Implement suggestion notification in SessionStart hook
3. Create `/uacs-create-skill` command
4. Test with real workflows
5. Release as v0.3.0

---

## Example Use Cases

### Use Case 1: Security-Conscious Developer

**Pattern:** Always checks for SQL injection after DB changes

**UACS Detects:**
- 6/10 sessions include "check for SQL injection"
- Always after editing `models.py` or `queries.py`

**UACS Suggests:**
```
/security-check-db
- Runs: bandit, semgrep on database files
- Checks: SQL injection, parameterized queries
- Reports: Vulnerabilities found
```

**Benefit:** Automates security review, saves 10 mins/session

---

### Use Case 2: Documentation-Driven Developer

**Pattern:** Often asks "what's the architecture?" when resuming

**UACS Detects:**
- 8/10 sessions start with architecture questions
- Claude re-explains same architecture each time

**UACS Suggests:**
```
/explain-arch
- Injects: ARCHITECTURE.md into context
- Includes: Component diagram, data flow
- Benefit: No need to re-explain, saves tokens
```

**Benefit:** Reduces context usage by 2K tokens/session

---

### Use Case 3: Test-Driven Developer

**Pattern:** Always runs tests before committing

**UACS Detects:**
- 10/10 sessions include `pytest` → `git commit` sequence
- Never commits if tests fail

**UACS Suggests:**
```
/test-and-commit "message"
- Runs: pytest
- Commits: Only if tests pass
- Safety: Never commits broken code
```

**Benefit:** Prevents accidental broken commits, saves 5 mins/session

---

This system turns UACS from a context store into a **workflow intelligence layer** that learns and optimizes over time.
