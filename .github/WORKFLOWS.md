# UACS Development Workflows

**Created:** 2026-01-31
**Purpose:** Document proven workflows and patterns for efficient development

---

## 1. Parallel Agent Workflow

### Pattern: Independent Feature Development

**When to Use:**
- Building 2+ independent features that touch different parts of the codebase
- Features have clear boundaries (different directories, minimal file overlap)
- Time-sensitive work where serial execution would be too slow

**How It Works:**

```bash
# Step 1: Launch multiple agents in parallel (single message, multiple Task calls)
# Agent 1: Build visualizer → src/uacs/visualization/
# Agent 2: Build demos → examples/tutorials/0X_*/

# Step 2: Let agents complete independently
# No worktrees needed if directory separation is clean

# Step 3: Test everything after completion
# Don't assume generated code is correct

# Step 4: Fix bugs systematically
# Search for patterns, fix globally

# Step 5: Commit in logical groups
# Fixes → Feature A → Feature B → Dependencies
```

**Key Success Factors:**
- ✅ Clear directory boundaries (zero file conflicts)
- ✅ Agents work on same branch (simpler than worktrees)
- ✅ Test EVERYTHING before committing
- ✅ Fix bugs in a separate commit before feature commits

**This Session's Results:**
- 2 agents running simultaneously
- 0 conflicts between agents
- ~30 files created across 2 workstreams
- 4 clean commits with logical grouping

---

## 2. Testing Strategy

### Pattern: Systematic Bug Discovery & Fix

**The Process:**

```bash
# 1. Test the "happy path" first
uv run python examples/tutorials/01_basic_setup/demo.py

# 2. When error occurs, identify the pattern
# Error: SharedContextManager.count_tokens() missing argument
# Pattern: Static method call instead of instance method

# 3. Search for ALL occurrences of the pattern
grep -r "SharedContextManager.count_tokens" examples/

# 4. Fix ALL occurrences in one pass
# Don't fix one at a time - you'll forget others

# 5. Test ALL affected files
for demo in examples/tutorials/0*/demo.py; do
    uv run python "$demo"
done

# 6. Commit fixes separately from feature work
git commit -m "fix: Correct method calls"
```

**Key Principles:**
- 🔍 **Search globally** - One bug often means many instances
- 🔧 **Fix globally** - Don't leave half-fixed code
- ✅ **Test everything** - Agent-generated code needs verification
- 📦 **Commit fixes first** - Separate bugs from features

---

## 3. Commit Strategy

### Pattern: Logical Grouping for Clear History

**The Order:**

```
1. Fixes (bugs found during testing)
2. Feature A (with docs)
3. Feature B (with docs)
4. Dependencies/Chores (lockfile updates, config changes)
```

**Why This Order:**
- Fixes show what was wrong with generated code
- Each feature is self-contained
- Dependencies come last (they're consequences of features)

**Example from This Session:**

```bash
# Commit 1: fix: Correct SharedContextManager.count_tokens() calls
# - Shows the bug pattern
# - Makes demos runnable
# - Small, focused, easy to review

# Commit 2: feat: Add 5 comprehensive demos with full documentation
# - 12 files, all demo-related
# - Can be reviewed as a unit
# - Includes all supporting docs

# Commit 3: feat: Add Context Graph Visualizer with real-time web UI
# - 13 files, all visualizer-related
# - Complete feature with tests
# - Self-contained

# Commit 4: chore: Add FastAPI/WebSocket dependencies
# - Consequence of visualizer feature
# - Lockfile updates
# - Keep separate from feature
```

**Commit Message Format:**
```
<type>: <short summary>

<body with details>
- Bullet points for key changes
- File counts and locations
- Technical details

[No Co-Authored-By unless explicitly requested]
```

---

## 4. Agent Output Validation

### Pattern: Trust But Verify

**Never Assume Agent Code Works:**

1. **Read the code** - Don't just trust the agent's claims
2. **Search for patterns** - If you find one bug, search for all instances
3. **Test systematically** - Run every demo, every test
4. **Check imports** - `from X import Y` might be wrong even if agent says it's right

**This Session's Bug:**
```python
# Agent wrote (WRONG):
from uacs.context.shared_context import SharedContextManager
token_count = SharedContextManager.count_tokens(context)

# Should be (RIGHT):
token_count = uacs.shared_context.count_tokens(context)
```

**Root Cause:**
- Agent incorrectly assumed static method
- Agent didn't test the code it generated
- Pattern repeated across 21 instances in 5 files

**Fix Strategy:**
- Found pattern in first demo
- Searched globally: `grep -r "SharedContextManager.count_tokens"`
- Fixed all 21 instances in one session
- Tested all 5 demos to verify

---

## 5. Documentation Integration

### Pattern: Docs Travel With Code

**The Rule:**
- Feature commits include ALL related documentation
- READMEs, guides, examples, API docs - everything together
- Makes features self-documenting in git history

**Example Structure:**
```
Commit: feat: Add comprehensive demos

Files:
├── examples/tutorials/01_basic_setup/
│   ├── demo.py          # Runnable code
│   ├── README.md        # Feature docs
│   └── output.txt       # Example output
├── examples/tutorials/02_context_compression/
│   ├── demo.py
│   ├── README.md
│   └── comparison.md    # Deep dive docs
└── docs/
    └── DEMOS.md         # Master guide
```

**Benefits:**
- Reviewers see code + docs together
- Features are complete when committed
- No orphaned documentation
- Git history is self-documenting

---

## 6. Todo List Management

### Pattern: Track Progress, Update Frequently

**The Process:**

```markdown
# At start of work session:
1. [in_progress] Fix demo bugs
2. [pending] Test all demos
3. [pending] Test visualizer
4. [pending] Commit everything

# After fixing bugs:
1. [completed] Fix demo bugs
2. [in_progress] Test all demos  ← MOVED
3. [pending] Test visualizer
4. [pending] Commit everything

# After testing:
1. [completed] Fix demo bugs
2. [completed] Test all demos
3. [completed] Test visualizer
4. [in_progress] Commit everything  ← MOVED
```

**Key Principles:**
- ✅ **Update immediately** after completing tasks
- 📋 **Break down complex tasks** into testable steps
- 🎯 **One in_progress** at a time (focus)
- 🗑️ **Remove completed items** when session ends (clean slate)

---

## 7. Testing State Handoff

### Pattern: Session Continuity Documents

**When Context Gets Too Large:**
1. Create `TESTING_STATE_YYYY-MM-DD.md`
2. Document:
   - What was completed
   - What's remaining
   - Bugs found and fixes needed
   - File inventory
   - Next steps with commands

**This Session's Example:**
```markdown
# TESTING_STATE_2026-01-31.md

## Current State
- Branch: refactor/minimal-package-manager
- 14 untracked files (needs testing & commit)

## Bug Found
Line 127 in examples/tutorials/01_basic_setup/demo.py:
SharedContextManager.count_tokens() missing argument

## Testing Plan
1. Fix bug in all 5 demos
2. Test each demo
3. Test visualizer
4. Commit in 3 logical groups

## Commands
```bash
uv run python examples/tutorials/01_basic_setup/demo.py
...
```

**Benefits:**
- New session can resume immediately
- No loss of context
- Clear action plan
- Reproducible steps

---

## 8. Key Lessons Learned

### What Worked Well

1. **Parallel Agents**
   - 2x faster than serial
   - Zero conflicts with good directory boundaries
   - Both agents delivered quality output

2. **Systematic Testing**
   - Found 21 bug instances across 5 files
   - Fixed globally in one pass
   - All demos work perfectly now

3. **Logical Commits**
   - Clear git history (fixes → features → deps)
   - Each commit is self-contained
   - Easy to review and revert if needed

4. **Documentation-First**
   - Every feature includes comprehensive docs
   - READMEs explain what/why/when/how
   - Examples are runnable and tested

### What to Avoid

1. **Don't Trust Agent Code Blindly**
   - Always test generated code
   - Search for pattern bugs globally
   - Agent claims ≠ working code

2. **Don't Batch Todo Updates**
   - Update after each task completion
   - Helps track progress accurately
   - Prevents forgotten tasks

3. **Don't Mix Fixes and Features**
   - Commit bug fixes separately
   - Makes review easier
   - Clearer git history

4. **Don't Skip Systematic Search**
   - One bug often means many instances
   - Fix all at once
   - Prevents "whack-a-mole" debugging

---

## 9. Workflow Checklist

### For Parallel Agent Work:

```markdown
☐ Define clear directory boundaries
☐ Launch agents in parallel (single message)
☐ Let agents complete fully
☐ Test EVERYTHING systematically
☐ Search for bug patterns globally
☐ Fix bugs before feature commits
☐ Commit in logical groups (fixes → features → deps)
☐ Verify clean working tree
☐ Update documentation
```

### For Bug Fixing:

```markdown
☐ Test to find first bug instance
☐ Identify the pattern
☐ Search globally (grep/Grep tool)
☐ Fix ALL instances in one pass
☐ Test ALL affected code
☐ Commit fix separately
☐ Proceed with feature work
```

### For Committing:

```markdown
☐ Stage fixes first
☐ Commit with clear message
☐ Stage feature A with docs
☐ Commit with comprehensive message
☐ Stage feature B with docs
☐ Commit with comprehensive message
☐ Stage dependencies/chores
☐ Commit final updates
☐ Verify: git status (clean)
```

---

## 10. Success Metrics

**This Session:**
- ⏱️ **Time:** ~2 hours (parallel) vs ~4 hours (serial) = 50% faster
- 🐛 **Bugs Found:** 21 instances across 5 files
- ✅ **Bugs Fixed:** 100% (all demos work)
- 📦 **Commits:** 4 logical, reviewable commits
- 📝 **Documentation:** ~20K words across demos + visualizer
- 🧪 **Tests:** 15 visualizer tests, all passing
- 🎯 **Working Tree:** Clean (only coverage.xml remains)

**Key Insight:**
> Parallel agent development + systematic testing + logical commits =
> Fast iteration with high quality output

---

## Future Application

**Use This Workflow When:**
1. Building multiple independent features
2. Time is critical (deadline/demo/release)
3. Features have clear boundaries
4. You need comprehensive documentation

**Adapt for:**
- Single-agent work (skip parallel steps)
- Smaller features (combine commits)
- Exploratory work (defer documentation)

**Always Keep:**
- Systematic testing
- Global bug searches
- Logical commit grouping
- Todo list tracking
- Documentation integration

---

**Document Version:** 1.0
**Last Updated:** 2026-01-31
**Next Review:** After next major feature development
