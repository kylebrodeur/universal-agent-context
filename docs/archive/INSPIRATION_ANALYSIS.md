# Repository Analysis: VibeKit, Deciduous, and Beans

## Executive Summary

Three complementary approaches to agent coordination that solve different but related problems:
- **VibeKit**: Secure execution isolation and observability
- **Deciduous**: Decision persistence and reasoning capture
- **Beans**: Flat-file task management with agent integration

Combined, they suggest a vision for **safe, observable, context-aware multi-agent orchestration** with persistent decision history.

---

## Individual Repository Analysis

### 1. InstructionKit (ai-config-kit) - IDE Configuration Distribution

**Repository**: https://github.com/troylar/ai-config-kit
**Language**: Python 3.10+ | **Distribution**: PyPI (instructionkit)

#### What It Does
InstructionKit (CLI: `inskit`) distributes IDE-specific content (rules, commands, hooks) across development teams via Git repositories, enabling consistent AI assistant configuration.

#### Key Innovations

1. **Multi-IDE Template Distribution**
   - Supports Claude Code, Cursor, GitHub Copilot, Windsurf
   - Templates include: rules, slash commands, hooks, configs
   - Git repos as distribution sources with `templatekit.yaml` manifests

2. **Namespace-based Installation**
   - Prevents conflicts when multiple sources install similar templates
   - Project-scope and global-scope installations
   - Example: `company/python-standards` vs `team/python-standards`

3. **Layered Configuration Model**
   ```
   Global (company-wide)
     ↓
   Team-specific
     ↓
   Project-specific
   ```
   All coexist with namespace prefixing, no overwrites

4. **Installation Tracking**
   - `template-installations.json` tracks what's installed
   - Enables team synchronization (commit file to repo)
   - Reproducible environments across developers

#### Template Manifest Example

```yaml
# templatekit.yaml
templates:
  - name: python-standards
    description: Python coding standards
    ide: claude
    files:
      - path: .claude/rules/python-standards.md
        type: instruction
        tags: [python, standards]

  - name: code-review-command
    description: Slash command for code review
    ide: claude
    files:
      - path: .claude/commands/review.md
        type: command
        tags: [review, quality]
```

#### How It Could Improve Multi-Agent CLI

**1. Shared Agent Instructions Repository**

Instead of each user configuring agents manually, teams share configurations:

```bash
# Install company-wide agent configurations
$ multi-agent config install https://github.com/company/agent-configs

# Installs to:
# .multi-agent/rules/company/security-review.md
# .multi-agent/rules/company/code-standards.md
# .multi-agent/commands/company/deploy.md
# .multi-agent/hooks/company/pre-commit-check.py
```

**2. Configuration Manifest for Workflows**

```yaml
# workflow-templates.yaml
workflows:
  - name: api-design
    description: Design REST API with architecture review
    agents: [claude, gemini]
    pattern: sequential
    context_profiles:
      claude:
        token_allocation:
          agents_md: 0.35
          conversation: 0.35
      gemini:
        token_allocation:
          skills: 0.40

  - name: security-audit
    description: Multi-agent security review
    agents: [claude, openai]
    pattern: parallel
    required_skills: [security-review, vulnerability-scan]
```

**3. Team Workflow Sharing**

```python
# New: WorkflowTemplateManager
class WorkflowTemplateManager:
    def install_from_git(self, repo_url: str, namespace: str):
        """Install workflow templates from Git repo."""
        repo = self._clone_or_pull(repo_url)
        manifest = self._load_manifest(repo / "workflow-templates.yaml")

        for workflow in manifest["workflows"]:
            # Install with namespace
            workflow_file = (
                self.templates_dir
                / namespace
                / f"{workflow['name']}.yaml"
            )
            workflow_file.write_text(yaml.dump(workflow))

        # Track installation
        self._record_installation(repo_url, namespace, manifest)

# Usage
$ multi-agent templates install https://github.com/company/workflows --namespace company

# Later in chat:
You: Use the company/api-design workflow for user authentication
[Loads template, applies to current task]
```

**4. Layered Agent Configurations**

Combine global company policies with team practices:

```python
class LayeredConfigLoader:
    def load_agent_config(self, agent_name: str) -> Dict:
        """Load layered agent configuration."""
        configs = []

        # 1. Global company config
        if (self.global_dir / f"{agent_name}.yaml").exists():
            configs.append(self._load_yaml(self.global_dir / f"{agent_name}.yaml"))

        # 2. Team config
        if (self.team_dir / f"{agent_name}.yaml").exists():
            configs.append(self._load_yaml(self.team_dir / f"{agent_name}.yaml"))

        # 3. Project config
        if (self.project_dir / f"{agent_name}.yaml").exists():
            configs.append(self._load_yaml(self.project_dir / f"{agent_name}.yaml"))

        # Merge (later configs override earlier)
        return self._deep_merge(configs)

# Example merged config:
# Global: "Never commit secrets" (hard rule)
# Team: "Use fastapi for APIs" (team preference)
# Project: "This project uses flask" (overrides team)
```

---

### 2. Kit - Code Intelligence and Context Building

**Repository**: https://github.com/cased/kit
**Language**: Python (86.5%), TypeScript (10.8%) | **Distribution**: PyPI (cased-kit)

#### What It Does
Kit provides production-grade infrastructure for code analysis and LLM context preparation, enabling developers to build code intelligence tools (reviewers, generators, analyzers).

#### Key Innovations

1. **Multi-layered Code Understanding**
   - File tree enumeration
   - Symbol extraction (functions, classes via AST)
   - Fast regex search (ripgrep integration)
   - Dependency graph generation
   - AI-powered summarization with search indexing

2. **Smart Context Preparation**
   - Chunk large files by lines or symbols
   - Reference-aware extraction (keeps definitions intact)
   - LLM-optimized output formatting
   - Line-based pinpoint lookups

3. **Multi-repository Support**
   - Unified interface for monorepos and microservices
   - Works with local and remote (GitHub) repositories
   - Analysis at specific commits/tags/branches
   - Incremental processing with caching

4. **MCP Server Integration**
   - Model Context Protocol (MCP) server for Claude
   - Function calling support
   - REST API interface
   - CLI for standalone operations

#### Architecture Patterns

```
┌──────────────────┐
│  CLI / MCP API   │  User interface
└─────────┬────────┘
          │
┌─────────▼────────┐
│  Repository      │  Local + GitHub abstraction
│  Abstraction     │
└─────────┬────────┘
          │
┌─────────▼────────┐
│  Analyzers       │  Symbol, dependency, context
└─────────┬────────┘
          │
┌─────────▼────────┐
│  Search Backend  │  Ripgrep + fallback
└─────────┬────────┘
          │
┌─────────▼────────┐
│  Cache Layer     │  Incremental extraction
└──────────────────┘
```

#### How It Could Improve Multi-Agent CLI

**1. Intelligent Codebase Context for Agents**

Instead of static AGENTS.md files, dynamically analyze codebases:

```python
# New: CodeIntelligenceAdapter
class CodeIntelligenceAdapter:
    def __init__(self, kit_client):
        self.kit = kit_client

    async def build_codebase_context(
        self,
        max_tokens: int,
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """Build intelligent codebase context for agents."""

        # 1. Extract project structure
        file_tree = await self.kit.list_files(
            repo_path=Path.cwd(),
            max_depth=3
        )

        # 2. Find relevant symbols
        if focus_areas:
            symbols = []
            for area in focus_areas:
                matches = await self.kit.search_symbols(
                    query=area,
                    symbol_types=["function", "class"]
                )
                symbols.extend(matches)
        else:
            # Get most important symbols (public APIs, entry points)
            symbols = await self.kit.extract_public_symbols()

        # 3. Get dependencies
        deps = await self.kit.analyze_dependencies()

        # 4. Build context within token budget
        context = self._format_context(
            file_tree=file_tree[:max_tokens//4],
            symbols=symbols[:max_tokens//4],
            dependencies=deps[:max_tokens//4],
            summaries=await self._get_summaries(symbols)
        )

        return context

# Usage in AgentContextAdapter
class AgentContextAdapter:
    def build_context(self, agent_name: str, user_query: str, ...):
        # Existing: AGENTS.md static content
        agents_context = self._get_project_context(...)

        # NEW: Dynamic code intelligence
        if self.kit_enabled:
            code_context = await self.code_intel.build_codebase_context(
                max_tokens=tokens["agents_md"],
                focus_areas=self._extract_focus_from_query(user_query)
            )
            agents_context = code_context  # Replace static with dynamic

        return context
```

**2. Symbol-aware Task Decomposition**

When designing workflows, understand what code actually exists:

```python
class WorkflowDesigner:
    async def design_workflow(self, user_task: str, ...):
        # NEW: Analyze codebase first
        relevant_code = await self.kit.search_code(user_task)

        # Enhance prompt with actual codebase knowledge
        prompt = self._build_design_prompt(
            user_task=user_task,
            available_agents=available_agents,
            codebase_analysis={
                "relevant_files": [f.path for f in relevant_code],
                "existing_patterns": await self.kit.find_similar_implementations(user_task),
                "dependencies": await self.kit.get_dependency_impact(relevant_code)
            }
        )

        # Orchestrator now knows actual codebase state
        recommendation = await self.design_agent.run_async(prompt)
```

**3. Context-Aware Agent Execution**

Give agents the exact code they need to see:

```python
async def execute_task(self, task: str, agent_names: List[str], ...):
    for agent_name in agent_names:
        # Build agent-specific context with code intelligence
        context = self.context_adapter.build_context(
            agent_name=agent_name,
            user_query=task,
            max_tokens=4000
        )

        # NEW: Add relevant code snippets
        if "implement" in task.lower() or "fix" in task.lower():
            code_snippets = await self.kit.extract_context_for_task(
                task_description=task,
                max_tokens=1000,
                include_definitions=True  # Keep function signatures intact
            )
            context += "\n\n# RELEVANT CODE\n" + code_snippets

        # Execute with enriched context
        result = await self._execute_agent(agent_name, task, context)
```

**4. Multi-repository Workflow Support**

For microservices or multi-repo projects:

```python
class MultiRepoOrchestrator(ChatOrchestrator):
    def __init__(self, registry, state_manager, monitor, repos: List[str]):
        super().__init__(registry, state_manager, monitor)
        self.kit_multi = KitMultiRepo(repos)

    async def handle_user_message(self, message: str):
        # Analyze across all repos
        affected_repos = await self.kit_multi.find_affected_repos(message)

        # Design workflow considering cross-repo dependencies
        workflow = await self.workflow_designer.design_workflow(
            user_task=message,
            cross_repo_context=await self.kit_multi.analyze_dependencies(affected_repos)
        )

        # Execute with repo-specific context per agent
        for phase in workflow.phases:
            repo_context = await self.kit_multi.get_repo_context(
                repo=affected_repos[phase.phase_number % len(affected_repos)],
                agent=phase.agent_name
            )
            # ... execute phase ...
```

**5. PR Review as a Workflow**

```python
# New command: multi-agent review-pr <pr-number>
async def review_pr(pr_number: int):
    """Multi-agent PR review using Kit for diff analysis."""

    # 1. Get PR diff via Kit
    pr_context = await kit.analyze_pr(
        pr_number=pr_number,
        include_tests=True,
        include_dependencies=True
    )

    # 2. Design review workflow
    workflow = await designer.design_workflow(
        user_task=f"Review PR #{pr_number}: {pr_context.title}",
        preferences={
            "focus": ["security", "performance", "test_coverage"],
            "agents": ["claude", "gemini"],  # Claude: architecture, Gemini: implementation
            "pattern": "parallel"  # Both review independently
        }
    )

    # 3. Execute reviews
    reviews = []
    for agent_name in workflow.agent_names:
        # Build context with actual changed code
        context = f"""
        # PR #{pr_number}: {pr_context.title}

        ## Changed Files
        {pr_context.changed_files}

        ## Diff
        {pr_context.diff}

        ## Dependencies Affected
        {pr_context.dependency_impact}

        ## Related Symbols
        {pr_context.related_symbols}
        """

        review = await orchestrator.execute_task(
            task="Provide code review feedback",
            agent_names=[agent_name],
            context=context
        )
        reviews.append(review)

    # 4. Post combined review to PR
    await kit.post_pr_comment(
        pr_number=pr_number,
        comment=format_review(reviews)
    )
```

---

### 3. VibeKit - Security & Observability Layer

**Repository**: https://github.com/superagent-ai/vibekit
**Stars**: 1.6k | **License**: MIT | **Language**: TypeScript (80%)

#### What It Does
VibeKit wraps AI coding agents (Claude Code, Gemini, Codex) in isolated Docker containers with automatic secret redaction and real-time observability.

#### Key Innovations

1. **Containerized Execution**
   - Agents run in isolated Docker containers
   - Zero risk to local filesystem
   - Clean, reproducible environments

2. **Automatic Secret Redaction**
   - Removes API keys, tokens from completions
   - Prevents credential leakage across agent boundaries
   - Built-in sensitive data filtering

3. **Real-time Observability**
   - Logs, traces, and metrics for agent operations
   - Debug visibility without exposing runtime internals
   - Local-first (no cloud dependencies)

4. **Universal Agent Support**
   - Works with Claude Code, Gemini CLI, Grok, Codex, OpenCode
   - CLI wrapper: `vibekit claude`
   - SDK for programmatic integration

#### Architecture Patterns

```
┌─────────────┐
│  CLI Layer  │  vibekit <agent> <command>
└──────┬──────┘
       │
┌──────▼──────┐
│  SDK Layer  │  @vibe-kit/sdk, @vibe-kit/auth
└──────┬──────┘
       │
┌──────▼──────┐
│  Execution  │  Docker isolation, code sandboxing
└──────┬──────┘
       │
┌──────▼──────┐
│Observability│  Logs, traces, metrics
└─────────────┘
```

#### How It Could Improve Multi-Agent CLI

**1. Security Enhancement**
- Wrap ADK agent servers in Docker containers
- Isolate each agent (claude, gemini, copilot, openai) in separate containers
- Prevent cross-contamination of context or credentials

**2. Secret Management**
```python
# New: SecureAgentServer wrapper
class SecureAgentServer:
    def __init__(self, agent_name: str, container_image: str):
        self.agent_name = agent_name
        self.container = DockerContainer(
            image=container_image,
            redact_patterns=[r'sk-[a-zA-Z0-9]{48}', r'ANTHROPIC_API_KEY=.*']
        )

    async def execute_task(self, task: str) -> str:
        # Run in container, auto-redact secrets
        result = await self.container.run(f"{self.agent_name} {task}")
        return self._redact_secrets(result)
```

**3. Observability Integration**
```python
# Add to monitor.py
class EnhancedMonitor(TerminalMonitor):
    def __init__(self):
        super().__init__()
        self.tracer = VibeKitTracer()

    async def log_agent_event(self, agent: str, event: str, data: Any):
        # Existing terminal logging
        await super().log_event(event, agent, data)

        # NEW: Send to observability backend
        self.tracer.record_span(
            agent=agent,
            operation=event,
            metadata=data,
            timestamp=datetime.now()
        )
```

**4. Risk Mitigation**
- Agents writing files? Happens in container, reviewed before merging to host
- Agent downloading dependencies? Isolated environment, no host compromise
- Malicious output? Caught by secret redaction before reaching user

---

### 2. Deciduous - Decision Graph & Reasoning Persistence

**Repository**: https://github.com/notactuallytreyanastasio/deciduous
**Stars**: ~300 | **License**: MIT | **Language**: Rust

#### What It Does
Deciduous captures the *reasoning behind code decisions* as a queryable graph that persists across sessions, survives context compression, and syncs across teammates.

#### Key Innovations

1. **Decision as First-Class Entities**
   ```
   Nodes: Goals, Decisions, Options, Actions, Outcomes, Observations
   Edges: leads_to, chosen, rejected, requires, blocks, enables
   ```

2. **Four View Modes**
   - **Chains**: Decision sequences (A → B → C)
   - **Timeline**: Merged with git commits
   - **Force-directed Graph**: Explore relationships
   - **DAG**: Hierarchical dependencies

3. **Persistent Session Context**
   - Decisions survive agent memory compaction
   - Queryable history: "Why did we reject approach X?"
   - Agents can learn from past failures

4. **Patch-Based Collaboration**
   - Export decisions as JSON patches
   - Commit alongside code changes
   - Teammates apply patches idempotently
   - Decisions flow through version control

5. **Git Integration**
   - Automatic branch detection
   - Commit linking
   - GitHub Pages deployment for visualization

#### Architecture Patterns

```
┌──────────────┐
│   CLI Tool   │  deciduous add/nodes/link/writeup
└──────┬───────┘
       │
┌──────▼───────┐
│ SQLite Graph │  Nodes + Edges with metadata
└──────┬───────┘
       │
┌──────▼───────┐
│Visualization │  Web viewer + Terminal UI
└──────┬───────┘
       │
┌──────▼───────┐
│ Export/Sync  │  JSON patches for collaboration
└──────────────┘
```

#### How It Could Improve Multi-Agent CLI

**1. Workflow Decision Tracking**
```python
# New: DecisionGraph integration
class WorkflowDesigner:
    def __init__(self, registry, conversation, decision_graph):
        self.registry = registry
        self.conversation = conversation
        self.decision_graph = decision_graph  # NEW

    async def design_workflow(self, user_task: str) -> WorkflowPlan:
        # Log the initial goal
        goal_id = self.decision_graph.add_node(
            type="goal",
            title=f"Design workflow for: {user_task}",
            confidence=100
        )

        # Get recommendation from orchestrator
        recommendation = await self.design_agent.run_async(prompt)

        # Log the decision
        decision_id = self.decision_graph.add_node(
            type="decision",
            title=f"Workflow: {', '.join(agent_names)} using {pattern}",
            description=recommendation,
            confidence=80
        )
        self.decision_graph.add_edge(goal_id, decision_id, "leads_to")

        # Log rejected alternatives
        for alternative in self._parse_alternatives(recommendation):
            alt_id = self.decision_graph.add_node(
                type="option",
                title=alternative["name"],
                description=alternative["reasoning"],
                confidence=alternative["score"]
            )
            self.decision_graph.add_edge(
                decision_id, alt_id,
                "rejected" if not alternative["chosen"] else "chosen"
            )

        return workflow_plan
```

**2. Split Test History**
```python
# Enhance SplitTestManager with decision tracking
class SplitTestManager:
    def __init__(self, test_storage_dir, decision_graph):
        self.test_storage_dir = test_storage_dir
        self.decision_graph = decision_graph  # NEW

    def run_test(self, test: SplitTest, executor_func) -> SplitTest:
        # Log split test as decision point
        decision_id = self.decision_graph.add_node(
            type="decision",
            title=f"A/B Test: {test.name}",
            description=test.task_description
        )

        # Run variants
        test = super().run_test(test, executor_func)

        # Log outcomes
        for variant in test.variants:
            outcome_id = self.decision_graph.add_node(
                type="outcome",
                title=f"{variant.name}: {variant.result.duration:.1f}s",
                description=f"Quality: {metrics['structure_score']}"
            )
            edge_type = "chosen" if variant.variant_id == test.winner_variant_id else "rejected"
            self.decision_graph.add_edge(decision_id, outcome_id, edge_type)

        return test
```

**3. Session Persistence Across Compaction**

The critical insight: **Chat conversations get compressed, but decisions should persist**

```python
# New: chat_orchestrator.py enhancement
class ChatOrchestrator:
    def __init__(self, registry, state_manager, monitor, decision_graph):
        # ... existing init
        self.decision_graph = decision_graph

    async def handle_user_message(self, message: str):
        # Track user intent as a goal
        goal_id = self.decision_graph.add_node(
            type="goal",
            title=message[:100],
            branch=self._get_current_branch()
        )

        result = await self._handle_design_phase(message)

        # Link workflow to goal
        if result["action"] == "workflow_designed":
            workflow_id = self.decision_graph.add_node(
                type="action",
                title=f"Workflow: {result['workflow_plan'].name}"
            )
            self.decision_graph.add_edge(goal_id, workflow_id, "leads_to")

        return result
```

**4. Queryable History for Agents**
```python
# When context is compressed, agents can query decision graph
context = self.context_adapter.build_context(
    agent_name="claude",
    user_query=query,
    conversation=conversation,
    max_tokens=4000
)

# NEW: Add decision history to context
recent_decisions = self.decision_graph.query(
    branch=current_branch,
    node_types=["decision", "goal"],
    limit=5
)

context += "\n\n# RECENT DECISIONS\n"
for decision in recent_decisions:
    context += f"- {decision.title}: {decision.description}\n"
    # Include chosen vs rejected options
    for edge in decision.outgoing_edges:
        if edge.type in ["chosen", "rejected"]:
            context += f"  {edge.type}: {edge.target.title}\n"
```

**5. Collaborative Decision Sync**
```bash
# After team discussion, export decisions
$ multi-agent decisions export --branch feature/chat-mode > decisions.json

# Teammate pulls branch and applies decisions
$ git pull origin feature/chat-mode
$ multi-agent decisions import decisions.json

# Agents now see full reasoning history
$ multi-agent chat
You: Why did we choose Gemini for the orchestrator?
[Agent queries decision graph, finds "chosen" edge with reasoning]
```

---

### 3. Beans - Flat-File Task Management with Agent Integration

**Repository**: https://github.com/hmans/beans
**Language**: Go (100%) | **License**: MIT

#### What It Does
Beans stores project tasks as Markdown files in `.beans/` directories, making them version-controlled and directly accessible to coding agents via a GraphQL query interface.

#### Key Innovations

1. **Version-Controlled Tasks**
   - Tasks stored as Markdown in `.beans/` directory
   - Git tracks task creation, updates, completion
   - No external task tracker needed

2. **Agent Hook System**
   ```
   SessionStart  → beans prime  → Emit agent instructions
   PreCompact    → beans prime  → Refresh task context
   ```

3. **GraphQL Query Engine**
   - Agents query specific fields to minimize tokens
   - Example: `{ beans(status: "open") { title description } }`
   - Efficient context building

4. **Self-Documenting Migrations**
   - Schema changes generate agent-executable prompts
   - Agents autonomously update their usage patterns
   - No manual documentation updates

5. **TUI Dashboard**
   - Terminal-based task browser
   - Vim-style navigation
   - Real-time task status

#### Architecture Patterns

```
┌─────────────┐
│   .beans/   │  Markdown files (version controlled)
└──────┬──────┘
       │
┌──────▼──────┐
│  GraphQL    │  Efficient querying interface
│   Engine    │
└──────┬──────┘
       │
┌──────▼──────┐
│   Hooks     │  SessionStart, PreCompact
│   System    │
└──────┬──────┘
       │
┌──────▼──────┐
│   Prime     │  Generate agent instructions
│  Command    │
└─────────────┘
```

#### How It Could Improve Multi-Agent CLI

**1. Workflow Tasks as Beans**
```bash
# Store workflow plans as tasks
$ multi-agent chat "Build REST API for todos"
[Workflow designed: claude → gemini]

# Automatically creates beans:
$ cat .beans/workflow-rest-api.md
```markdown
# Workflow: REST API for todos
Status: pending
Agents: claude, gemini
Pattern: sequential

## Phase 1: Architecture (claude)
- [ ] Design API endpoints
- [ ] Define data models
- [ ] Security considerations

## Phase 2: Implementation (gemini)
- [ ] Implement endpoints
- [ ] Write tests
- [ ] Documentation
```

**2. Hook Integration for Context Priming**
```python
# New: BeansAdapter for multi-agent-cli
class BeansAdapter:
    def __init__(self, beans_dir: Path = Path.cwd() / ".beans"):
        self.beans_dir = beans_dir
        self.graphql_engine = BeansGraphQL(beans_dir)

    def prime_agent_context(self, agent_name: str, phase: str) -> str:
        """Generate agent-specific context from beans."""
        query = """
        {
          beans(status: "open", assignee: "%s") {
            title
            description
            priority
            dependencies {
              title
              status
            }
          }
        }
        """ % agent_name

        tasks = self.graphql_engine.execute(query)

        if phase == "design":
            return self._format_design_context(tasks)
        elif phase == "execution":
            return self._format_execution_context(tasks)
        else:
            return self._format_general_context(tasks)
```

**3. Workflow Phase Tracking**
```python
# Integrate with ChatOrchestrator
class ChatOrchestrator:
    def __init__(self, registry, state_manager, monitor, beans):
        # ... existing
        self.beans = beans  # NEW

    async def approve_workflow(self):
        # Create bean for each workflow phase
        for phase in self.workflow_plan.phases:
            self.beans.create_task(
                title=f"Phase {phase.phase_number}: {phase.agent_name}",
                description=phase.task_description,
                status="pending",
                assignee=phase.agent_name,
                metadata={
                    "workflow_id": self.workflow_plan.id,
                    "depends_on": phase.depends_on
                }
            )

        # Execute workflow
        result = await self._execute_workflow()

        # Update task statuses
        for phase in self.workflow_plan.phases:
            self.beans.update_task_status(
                f"Phase {phase.phase_number}",
                "completed"
            )

        return result
```

**4. Agent-Specific Task Queries**
```python
# When building agent context
class AgentContextAdapter:
    def build_context(
        self,
        agent_name: str,
        user_query: str,
        conversation: ConversationManager,
        max_tokens: int = 4000
    ) -> str:
        # Existing context building
        context = self._build_base_context(...)

        # NEW: Add relevant tasks from beans
        agent_tasks = self.beans.query_tasks(
            assignee=agent_name,
            status=["open", "in_progress"],
            max_results=5
        )

        if agent_tasks:
            context += "\n\n# YOUR CURRENT TASKS\n"
            for task in agent_tasks:
                context += f"\n## {task.title}\n"
                context += f"{task.description}\n"
                if task.dependencies:
                    context += "Depends on:\n"
                    for dep in task.dependencies:
                        context += f"  - [{dep.status}] {dep.title}\n"

        return context
```

**5. Migration-Driven Evolution**
```python
# When workflow plan schema changes
class WorkflowPlanMigration:
    @staticmethod
    def v2_to_v3_migration():
        """Add agent context configs to workflow plans."""
        migration_bean = Beans.create_migration_task(
            title="Update workflow plans to include agent_context_configs",
            instructions="""
            The WorkflowPlan schema now includes:
            - agent_context_configs: Dict[str, Dict[str, Any]]

            When designing workflows, you should now specify:
            workflow_plan.agent_context_configs = {
                "claude": {"token_allocation": {"conversation": 0.40}},
                "gemini": {"token_allocation": {"skills": 0.50}}
            }
            """,
            auto_executable=True
        )

        # Agents see this bean at SessionStart, update their behavior
        return migration_bean
```

---

## Cross-Repository Synergies

### Synergy 1: **Safe Decision Persistence**

**Combination**: VibeKit + Deciduous

**Problem**: Agents making decisions need isolation (security) AND historical context (persistence).

**Solution**:
- Run agents in VibeKit containers for safety
- Store their decision reasoning in Deciduous graph
- Even if container is destroyed, decisions persist

```python
class SecureDecisionOrchestrator:
    def __init__(self, vibekit_wrapper, decision_graph):
        self.vibekit = vibekit_wrapper
        self.decisions = decision_graph

    async def execute_with_decision_tracking(self, agent: str, task: str):
        # Log intent
        goal_id = self.decisions.add_node(type="goal", title=task)

        # Execute in isolated container
        result = await self.vibekit.run_agent_in_container(
            agent=agent,
            task=task,
            redact_secrets=True
        )

        # Log outcome (persists even after container cleanup)
        outcome_id = self.decisions.add_node(
            type="outcome",
            title=f"{agent} completed: {task[:50]}",
            description=result.summary
        )
        self.decisions.add_edge(goal_id, outcome_id, "leads_to")

        return result
```

### Synergy 2: **Observable Task Execution**

**Combination**: VibeKit + Beans

**Problem**: Need visibility into what agents are doing while maintaining task context.

**Solution**:
- Beans defines what to do (tasks)
- VibeKit shows what's happening (observability)
- Combined: Real-time task execution monitoring

```python
class ObservableTaskExecution:
    def __init__(self, beans, vibekit_tracer):
        self.beans = beans
        self.tracer = vibekit_tracer

    async def execute_task(self, task_id: str, agent: str):
        task = self.beans.get_task(task_id)

        # Start trace span
        with self.tracer.start_span(f"task-{task_id}") as span:
            span.set_attribute("agent", agent)
            span.set_attribute("task_title", task.title)

            # Update bean status
            self.beans.update_task(task_id, status="in_progress")

            # Execute
            result = await self._run_agent(agent, task.description)

            # Log metrics
            span.set_attribute("tokens_used", result.tokens)
            span.set_attribute("duration_sec", result.duration)

            # Complete task
            self.beans.update_task(
                task_id,
                status="completed",
                result=result.output
            )

            return result
```

### Synergy 3: **Decision-Driven Task Management**

**Combination**: Deciduous + Beans

**Problem**: Tasks exist, but the *reasoning* behind prioritization is lost.

**Solution**:
- Deciduous tracks *why* a task is important
- Beans tracks *what* needs doing
- Link them: Tasks reference decisions, decisions spawn tasks

```python
class DecisionTaskBridge:
    def __init__(self, decision_graph, beans):
        self.decisions = decision_graph
        self.beans = beans

    def decision_to_tasks(self, decision_id: str):
        """When decision is made, create corresponding tasks."""
        decision = self.decisions.get_node(decision_id)

        # Find chosen options
        chosen_options = [
            edge.target for edge in decision.outgoing_edges
            if edge.type == "chosen"
        ]

        # Create tasks for each chosen option
        for option in chosen_options:
            task_id = self.beans.create_task(
                title=option.title,
                description=option.description,
                metadata={
                    "decision_id": decision_id,
                    "decision_title": decision.title,
                    "confidence": option.confidence
                }
            )

            # Link back to decision graph
            task_node = self.decisions.add_node(
                type="action",
                title=f"Task: {option.title}",
                external_id=task_id
            )
            self.decisions.add_edge(decision_id, task_node, "enables")

    def query_task_reasoning(self, task_id: str) -> str:
        """Given a task, explain why it exists."""
        task = self.beans.get_task(task_id)
        decision_id = task.metadata.get("decision_id")

        if not decision_id:
            return "No decision context available"

        # Trace back through decision graph
        decision = self.decisions.get_node(decision_id)
        reasoning_path = self.decisions.trace_back_to_goal(decision_id)

        explanation = f"Task '{task.title}' exists because:\n\n"
        for i, node in enumerate(reasoning_path):
            explanation += f"{i+1}. {node.type}: {node.title}\n"
            explanation += f"   {node.description}\n\n"

        return explanation
```

### Synergy 4: **Complete Multi-Agent Workflow System**

**Combination**: VibeKit + Deciduous + Beans

**The Vision**: Safe, observable, context-aware orchestration with persistent reasoning.

```
User Request
     │
     ▼
┌────────────────────┐
│ ChatOrchestrator   │  Handle user message
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ WorkflowDesigner   │  Design agent workflow
│  + Deciduous       │  Track design decisions
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Beans              │  Create workflow phase tasks
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ VibeKit Executor   │  Run agents in containers
│  + Observability   │  Real-time monitoring
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ AgentContextAdapter│  Build agent-specific context
│  + Decision Query  │  Include past reasoning
│  + Task Query      │  Include current tasks
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Agent Execution    │  Isolated, observable work
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Result Collection  │  Gather outputs
│  + Decision Log    │  Record outcomes
│  + Task Update     │  Mark complete
└────────────────────┘
```

#### Example Flow

```python
# User initiates chat
$ multi-agent chat "Build user authentication system"

# 1. DECISION TRACKING (Deciduous)
goal_id = decisions.add_node(
    type="goal",
    title="Build user authentication system",
    branch="feature/auth-system"
)

# 2. WORKFLOW DESIGN
workflow = await designer.design_workflow(task)
# Orchestrator recommends: claude (architecture) → gemini (implementation)

decision_id = decisions.add_node(
    type="decision",
    title="Sequential workflow: claude → gemini",
    description="Claude best for security architecture, Gemini for code"
)
decisions.add_edge(goal_id, decision_id, "leads_to")

# 3. TASK CREATION (Beans)
beans.create_task(
    title="Phase 1: Security architecture (claude)",
    description="Design authentication flow, token management, session handling",
    assignee="claude",
    metadata={"workflow_id": workflow.id, "decision_id": decision_id}
)

beans.create_task(
    title="Phase 2: Implementation (gemini)",
    description="Implement JWT tokens, password hashing, session management",
    assignee="gemini",
    depends_on=["Phase 1"],
    metadata={"workflow_id": workflow.id}
)

# 4. SECURE EXECUTION (VibeKit)
with vibekit.start_trace("auth-system-workflow"):
    # Execute Phase 1 in container
    claude_result = await vibekit.run_in_container(
        agent="claude",
        task=beans.get_task("Phase 1"),
        context=context_adapter.build_context(
            agent_name="claude",
            query="Design authentication system",
            # Includes recent decisions from Deciduous
            # Includes current tasks from Beans
        ),
        redact_secrets=True
    )

    # Log outcome
    outcome_id = decisions.add_node(
        type="outcome",
        title="Authentication architecture designed",
        description=claude_result.summary
    )
    decisions.add_edge(decision_id, outcome_id, "leads_to")

    # Update task
    beans.update_task("Phase 1", status="completed", result=claude_result.output)

    # Execute Phase 2 with context from Phase 1
    gemini_result = await vibekit.run_in_container(
        agent="gemini",
        task=beans.get_task("Phase 2"),
        context=context_adapter.build_context(
            agent_name="gemini",
            query=f"Implement: {claude_result.output}",
            previous_outputs=[claude_result]
        )
    )

    beans.update_task("Phase 2", status="completed")

# 5. QUERY REASONING (months later)
$ multi-agent decisions query "authentication"
Found decision: "Sequential workflow: claude → gemini"
Reasoning: "Claude best for security architecture, Gemini for code"
Alternatives considered:
  ✓ chosen: Sequential claude→gemini (confidence: 85%)
  ✗ rejected: Parallel all agents (confidence: 40%, reason: "security needs careful thought")
  ✗ rejected: Single agent (confidence: 55%, reason: "benefits from architecture+implementation split")

$ beans show "Phase 1"
# Phase 1: Security architecture (claude)
Status: completed
Decision: feature/auth-system/sequential-workflow-claude-gemini
Result: [Architecture document with JWT flow, token storage, session management...]
```

---

## Implementation Roadmap

### Phase 1: Foundation (Deciduous Integration)

**Goal**: Add decision persistence to existing workflow designer.

**Tasks**:
1. Add Deciduous as dependency (or reimplement graph in Python)
2. Extend `WorkflowDesigner` to log decisions
3. Extend `SplitTestManager` to track test outcomes
4. Add `multi-agent decisions` command to CLI
5. Integrate decision query into `AgentContextAdapter`

**Files to Create**:
- `src/multi_agent_cli/decision_graph.py` - Graph storage and query
- `src/multi_agent_cli/decisions_cli.py` - CLI commands
- `.multi-agent/decisions/` - Local decision storage directory

**Estimated Effort**: 2-3 days

### Phase 2: Task Management (Beans Integration)

**Goal**: Version-controlled workflow tasks.

**Tasks**:
1. Add Beans-style task storage in `.beans/`
2. Create `BeansAdapter` for task management
3. Workflow phases automatically create tasks
4. Agent context includes current tasks
5. Add `multi-agent tasks` command to CLI

**Files to Create**:
- `src/multi_agent_cli/beans_adapter.py` - Task storage interface
- `src/multi_agent_cli/tasks_cli.py` - CLI commands
- `.beans/` - Markdown task files

**Estimated Effort**: 2-3 days

### Phase 3: Secure Execution (VibeKit Integration)

**Goal**: Container isolation and observability.

**Tasks**:
1. Add Docker support to agent servers
2. Implement `SecureAgentServer` wrapper
3. Add secret redaction to responses
4. Implement observability layer (traces, metrics)
5. Add `multi-agent trace` command for viewing execution

**Files to Create**:
- `src/multi_agent_cli/secure_executor.py` - Container execution
- `src/multi_agent_cli/observability.py` - Tracing and metrics
- `docker/` - Dockerfiles for each agent
- `src/multi_agent_cli/trace_cli.py` - Trace viewing commands

**Estimated Effort**: 3-4 days

### Phase 4: Integration & Polish

**Goal**: Unified experience across all three systems.

**Tasks**:
1. Connect decisions → tasks → execution
2. Build unified dashboard showing all three layers
3. Add export/import for team collaboration
4. Write comprehensive documentation
5. Create example workflows

**Estimated Effort**: 2-3 days

**Total Estimated Effort**: 9-13 days

---

## Quick Wins (Implement First)

### 1. Decision Tracking (Deciduous-inspired)

**Why**: Immediate value, low complexity, enhances existing split testing.

```python
# Minimal implementation in ~200 lines
class SimpleDecisionGraph:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.nodes = {}
        self.edges = []

    def add_node(self, type: str, title: str, **kwargs) -> str:
        node_id = str(uuid.uuid4())[:8]
        self.nodes[node_id] = {
            "id": node_id,
            "type": type,
            "title": title,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self._save()
        return node_id

    def add_edge(self, source: str, target: str, type: str):
        self.edges.append({"source": source, "target": target, "type": type})
        self._save()

    def query(self, **filters) -> List[Dict]:
        # Simple filtering
        results = list(self.nodes.values())
        for key, value in filters.items():
            results = [n for n in results if n.get(key) == value]
        return results

    def _save(self):
        with open(self.storage_dir / "graph.json", 'w') as f:
            json.dump({"nodes": self.nodes, "edges": self.edges}, f, indent=2)
```

**Immediate Benefit**: Split test results now have persistent reasoning history.

### 2. Task Files (Beans-inspired)

**Why**: Simple Markdown files, no complex dependencies, immediate value for team collaboration.

```python
# Minimal implementation in ~150 lines
class TaskManager:
    def __init__(self, beans_dir: Path = Path(".beans")):
        self.beans_dir = beans_dir
        self.beans_dir.mkdir(exist_ok=True)

    def create_task(self, title: str, description: str, **metadata):
        slug = title.lower().replace(" ", "-")[:50]
        task_file = self.beans_dir / f"{slug}.md"

        content = f"""# {title}

Status: pending

{description}

## Metadata
```json
{json.dumps(metadata, indent=2)}
```
"""
        task_file.write_text(content)
        return str(task_file)

    def list_tasks(self, status: Optional[str] = None) -> List[Dict]:
        tasks = []
        for task_file in self.beans_dir.glob("*.md"):
            content = task_file.read_text()
            # Parse front matter and content
            task = self._parse_task(content, task_file.name)
            if status is None or task["status"] == status:
                tasks.append(task)
        return tasks
```

**Immediate Benefit**: Workflow phases visible as Markdown files in version control.

### 3. Secret Redaction (VibeKit-inspired)

**Why**: Security-critical, simple regex-based implementation, no Docker required initially.

```python
# Minimal implementation in ~100 lines
class SecretRedactor:
    PATTERNS = [
        (r'sk-[a-zA-Z0-9]{48}', '<OPENAI_API_KEY>'),
        (r'ANTHROPIC_API_KEY=.*', 'ANTHROPIC_API_KEY=<REDACTED>'),
        (r'Bearer [a-zA-Z0-9._-]+', 'Bearer <REDACTED>'),
        (r'password["\s:=]+[^"\s]+', 'password=<REDACTED>'),
    ]

    def redact(self, text: str) -> str:
        for pattern, replacement in self.PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

# Add to agent servers
class ClaudeAgentServer:
    def __init__(self, port: int):
        self.redactor = SecretRedactor()  # NEW
        # ... existing init

    async def execute_task(self, task: str) -> str:
        result = await self._run_claude(task)
        return self.redactor.redact(result)  # NEW
```

**Immediate Benefit**: Prevents accidental credential leakage in agent responses.

---

## Architectural Recommendations

### 1. Layered Design

```
┌─────────────────────────────────────┐
│  CLI Layer (typer commands)         │  User interface
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  Orchestration Layer                │  ChatOrchestrator, WorkflowDesigner
│   + DecisionGraph                   │
│   + TaskManager                     │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  Execution Layer                    │  ADKOrchestrator, AgentServers
│   + SecureExecutor (VibeKit)        │
│   + Observability                   │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│  Storage Layer                      │  StateManager, DecisionGraph, Beans
└─────────────────────────────────────┘
```

### 2. Plugin Architecture

Make each enhancement optional:

```python
# pyproject.toml
[project.optional-dependencies]
decisions = ["networkx>=3.0"]  # For decision graphs
tasks = []  # Pure Python, no deps
security = ["docker>=6.0"]  # For container execution
observability = ["opentelemetry-api>=1.20"]  # For tracing
full = ["multi-agent-cli[decisions,tasks,security,observability]"]

# Usage
$ pip install multi-agent-cli  # Core only
$ pip install multi-agent-cli[decisions]  # + decision tracking
$ pip install multi-agent-cli[full]  # Everything
```

### 3. Hooks System (Beans-inspired)

```python
# New: src/multi_agent_cli/hooks.py
class HookRegistry:
    def __init__(self):
        self.hooks = {
            "session_start": [],
            "pre_compact": [],
            "post_execution": [],
            "workflow_designed": [],
        }

    def register(self, event: str, callback: Callable):
        self.hooks[event].append(callback)

    async def trigger(self, event: str, **context):
        for callback in self.hooks[event]:
            await callback(**context)

# Usage in ChatOrchestrator
class ChatOrchestrator:
    def __init__(self, registry, state_manager, monitor, hooks):
        self.hooks = hooks

    async def start_session(self, initial_task: str):
        session_id = self.state_manager.create_session(initial_task, "chat")

        # Trigger hooks
        await self.hooks.trigger(
            "session_start",
            session_id=session_id,
            task=initial_task
        )

        return session_id

# Plugin can register:
def on_session_start(session_id: str, task: str):
    """Create initial task in beans."""
    beans.create_task(
        title=task,
        description=f"Session {session_id}",
        status="in_progress"
    )

hooks.register("session_start", on_session_start)
```

---

## Key Takeaways

### What Each Project Teaches Us

1. **VibeKit**: Security and observability are not afterthoughts—they should be architectural pillars.

2. **Deciduous**: Decisions are first-class data. If you can't query "why did we do X?", you'll repeat mistakes.

3. **Beans**: Agent integration is about hooks and queries, not tight coupling. Let agents pull context when needed.

### The Unified Vision

**Current State**: Multi-agent orchestration with context adaptation and split testing.

**Future State**: Safe, observable, decision-aware orchestration where:
- Agents run in isolated containers (VibeKit)
- Every decision is queryable months later (Deciduous)
- Tasks are version-controlled and agent-accessible (Beans)
- Split tests create persistent learning history
- Team members share reasoning, not just code

### Implementation Priority

1. **Decision tracking** (Deciduous) - Most valuable, easiest to implement
2. **Task management** (Beans) - Improves collaboration, simple Markdown files
3. **Secret redaction** (VibeKit) - Security-critical, regex-based is quick
4. **Full isolation** (VibeKit containers) - Requires Docker, more complex
5. **Observability** (VibeKit traces) - Nice-to-have, can use existing monitor

---

## Next Steps

### Immediate Actions

1. **Prototype decision tracking**: Add `SimpleDecisionGraph` to `WorkflowDesigner`
2. **Test with split tests**: Log split test outcomes as decisions
3. **Query in chat**: When user asks "why X?", query decision graph
4. **Measure value**: Does it help with context? Decision replay?

### Week 1 Goals

- [ ] Decision graph integrated with WorkflowDesigner
- [ ] Split tests create persistent decision nodes
- [ ] `multi-agent decisions query` command working
- [ ] Agent context includes recent decisions

### Month 1 Goals

- [ ] Task files created for workflow phases
- [ ] Secret redaction in agent responses
- [ ] Team can share decisions via git
- [ ] Dashboard shows decisions + tasks + execution

---

*Generated: 2025-12-15*
*Analysis of: VibeKit, Deciduous, Beans*
*For: Multi-Agent CLI Project*
