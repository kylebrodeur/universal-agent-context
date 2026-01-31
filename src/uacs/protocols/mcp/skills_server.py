"""MCP Tools Server for Skills & Context Management.

Exposes all unified context capabilities as MCP tools following
the Model Context Protocol specification.

Spec: https://modelcontextprotocol.io/specification/
"""

import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

# Initialize server
server = Server("uacs-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        # Skills Management
        Tool(
            name="skills_list",
            description="List all available agent skills",
            inputSchema={
                "type": "object",
                "properties": {
                    "skills_file": {
                        "type": "string",
                        "description": "Optional path to skills file or directory",
                    }
                },
            },
        ),
        Tool(
            name="skills_show",
            description="Show detailed information about a specific skill",
            inputSchema={
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Name of the skill to show",
                    },
                    "skills_file": {
                        "type": "string",
                        "description": "Optional path to skills file or directory",
                    },
                },
                "required": ["skill_name"],
            },
        ),
        Tool(
            name="skills_test_trigger",
            description="Test which skill would be triggered by a query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query to test"},
                    "skills_file": {
                        "type": "string",
                        "description": "Optional path to skills file or directory",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="skills_validate",
            description="Validate agent skills file format",
            inputSchema={
                "type": "object",
                "properties": {
                    "skills_file": {
                        "type": "string",
                        "description": "Path to skills file (SKILL.md or directory)",
                    }
                },
            },
        ),
        # Context Management
        Tool(
            name="context_stats",
            description="Get context and token usage statistics",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="context_get_compressed",
            description="Get compressed context within token budget",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "Filter by agent name (optional)",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens to return",
                        "default": 4000,
                    },
                },
            },
        ),
        Tool(
            name="context_add_entry",
            description="Add a new context entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Context content"},
                    "agent": {"type": "string", "description": "Agent name"},
                    "references": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Referenced entry IDs",
                    },
                },
                "required": ["content", "agent"],
            },
        ),
        Tool(
            name="context_compress",
            description="Manually trigger context compression",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="context_graph",
            description="Get context relationship graph",
            inputSchema={"type": "object", "properties": {}},
        ),
        # AGENTS.md Management
        Tool(
            name="agents_md_load",
            description="Load and parse AGENTS.md file",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_root": {
                        "type": "string",
                        "description": "Project root directory",
                    }
                },
            },
        ),
        Tool(
            name="agents_md_to_prompt",
            description="Convert AGENTS.md to system prompt",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_root": {
                        "type": "string",
                        "description": "Project root directory",
                    }
                },
            },
        ),
        # Unified Context
        Tool(
            name="unified_build_prompt",
            description="Build complete agent prompt with all context sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_query": {"type": "string", "description": "User's query"},
                    "agent_name": {
                        "type": "string",
                        "description": "Agent receiving the prompt",
                    },
                    "include_history": {
                        "type": "boolean",
                        "description": "Include shared context history",
                        "default": True,
                    },
                    "max_context_tokens": {
                        "type": "integer",
                        "description": "Max tokens for context",
                        "default": 4000,
                    },
                },
                "required": ["user_query", "agent_name"],
            },
        ),
        Tool(
            name="unified_capabilities",
            description="Get all unified capabilities (Agent Skills + AGENTS.md + Context)",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="unified_token_stats",
            description="Get token usage statistics across all sources",
            inputSchema={"type": "object", "properties": {}},
        ),
        # Package Management
        Tool(
            name="install_package",
            description="Install package from GitHub, Git URL, or local path",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Package source (owner/repo, git URL, or local path)",
                    },
                    "validate": {
                        "type": "boolean",
                        "description": "Whether to validate before installing",
                        "default": True,
                    },
                },
                "required": ["source"],
            },
        ),
        Tool(
            name="list_installed_packages",
            description="List all installed packages",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="validate_package",
            description="Validate a package without installing",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Package source to validate",
                    },
                },
                "required": ["source"],
            },
        ),
        # Project Validation
        Tool(
            name="project_validate",
            description="Validate AGENTS.md and agent skills configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_root": {
                        "type": "string",
                        "description": "Project root directory",
                    },
                    "include_suggestions": {
                        "type": "boolean",
                        "description": "Include suggestions in report",
                        "default": True,
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool invocation."""
    from uacs.adapters.agent_skill_adapter import AgentSkillAdapter
    from uacs.adapters.agents_md_adapter import AgentsMDAdapter
    from uacs.context.unified_context import UnifiedContextAdapter
    from uacs.packages import PackageManager
    from uacs.cli.utils import get_project_root

    # Skills Management Tools
    if name == "skills_list":
        adapters = AgentSkillAdapter.discover_skills(get_project_root())
        skills = [a.parsed.name for a in adapters if a.parsed]
        return [TextContent(type="text", text=json.dumps({"skills": skills}, indent=2))]

    if name == "skills_show":
        adapters = AgentSkillAdapter.discover_skills(get_project_root())
        skill_name = arguments["skill_name"]
        for adapter in adapters:
            if adapter.parsed and adapter.parsed.name == skill_name:
                return [
                    TextContent(
                        type="text",
                        text=adapter.to_system_prompt(),
                    )
                ]
        return [TextContent(type="text", text=f"Skill '{skill_name}' not found")]

    if name == "skills_test_trigger":
        adapters = AgentSkillAdapter.discover_skills(get_project_root())
        query = arguments["query"].lower()
        matched_skill = None

        for adapter in adapters:
            if adapter.parsed and hasattr(adapter.parsed, "triggers"):
                for trigger in adapter.parsed.triggers:
                    if trigger.lower() in query or query in trigger.lower():
                        matched_skill = adapter.parsed
                        break
            if matched_skill:
                break

        if matched_skill:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "matched": True,
                            "skill_name": matched_skill.name,
                            "triggers": matched_skill.triggers,
                        },
                        indent=2,
                    ),
                )
            ]
        return [TextContent(type="text", text=json.dumps({"matched": False}, indent=2))]

    if name == "skills_validate":
        adapters = AgentSkillAdapter.discover_skills(get_project_root())
        issues = []
        skill_count = 0
        for adapter in adapters:
            if adapter.parsed:
                skill_count += 1
                if not adapter.parsed.description:
                    issues.append(f"Skill '{adapter.parsed.name}': Missing description")
                if (
                    not hasattr(adapter.parsed, "triggers")
                    or not adapter.parsed.triggers
                ):
                    issues.append(f"Skill '{adapter.parsed.name}': No triggers")

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "valid": len(issues) == 0,
                        "skill_count": skill_count,
                        "issues": issues,
                    },
                    indent=2,
                ),
            )
        ]

    # Context Management Tools
    if name == "context_stats":
        context_adapter = UnifiedContextAdapter()
        stats = context_adapter.get_token_stats()
        return [TextContent(type="text", text=json.dumps(stats, indent=2))]

    if name == "context_get_compressed":
        context_adapter = UnifiedContextAdapter()
        context = context_adapter.shared_context.get_compressed_context(
            agent=arguments.get("agent"), max_tokens=arguments.get("max_tokens", 4000)
        )
        return [TextContent(type="text", text=context)]

    if name == "context_add_entry":
        context_adapter = UnifiedContextAdapter()
        entry_id = context_adapter.shared_context.add_entry(
            content=arguments["content"],
            agent=arguments["agent"],
            references=arguments.get("references", []),
        )
        return [
            TextContent(type="text", text=json.dumps({"entry_id": entry_id}, indent=2))
        ]

    if name == "context_compress":
        context_adapter = UnifiedContextAdapter()
        before = context_adapter.shared_context.get_stats()
        context_adapter.optimize_context()
        after = context_adapter.shared_context.get_stats()

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "before_tokens": before["total_tokens"],
                        "after_tokens": after["total_tokens"],
                        "saved": before["total_tokens"] - after["total_tokens"],
                    },
                    indent=2,
                ),
            )
        ]

    if name == "context_graph":
        context_adapter = UnifiedContextAdapter()
        graph = context_adapter.shared_context.get_context_graph()
        return [TextContent(type="text", text=json.dumps(graph, indent=2))]

    # AGENTS.md Tools
    if name == "agents_md_load":
        agents_adapter = AgentsMDAdapter(
            Path(arguments.get("project_root"))
            if arguments.get("project_root")
            else None
        )
        if agents_adapter.config:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(agents_adapter.to_adk_capabilities(), indent=2),
                )
            ]
        return [TextContent(type="text", text="AGENTS.md not found")]

    if name == "agents_md_to_prompt":
        agents_adapter = AgentsMDAdapter(
            Path(arguments.get("project_root"))
            if arguments.get("project_root")
            else None
        )
        prompt = agents_adapter.to_system_prompt()
        return [TextContent(type="text", text=prompt)]

    # Unified Context Tools
    if name == "unified_build_prompt":
        context_adapter = UnifiedContextAdapter()
        prompt = context_adapter.build_agent_prompt(
            user_query=arguments["user_query"],
            agent_name=arguments["agent_name"],
            include_history=arguments.get("include_history", True),
            max_context_tokens=arguments.get("max_context_tokens", 4000),
        )
        return [TextContent(type="text", text=prompt)]

    if name == "unified_capabilities":
        context_adapter = UnifiedContextAdapter()
        caps = context_adapter.get_unified_capabilities()
        return [TextContent(type="text", text=json.dumps(caps, indent=2))]

    if name == "unified_token_stats":
        context_adapter = UnifiedContextAdapter()
        stats = context_adapter.get_token_stats()
        return [TextContent(type="text", text=json.dumps(stats, indent=2))]

    # Package Management Tools
    if name == "install_package":
        project_path = get_project_root()
        manager = PackageManager(project_path)
        try:
            package = manager.install(
                arguments["source"],
                validate=arguments.get("validate", True)
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "installed": True,
                            "package_name": package.name,
                            "version": package.version,
                            "path": str(package.path),
                        },
                        indent=2,
                    ),
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"installed": False, "error": str(e)},
                        indent=2,
                    ),
                )
            ]

    if name == "list_installed_packages":
        project_path = get_project_root()
        manager = PackageManager(project_path)
        packages = manager.list_installed()
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    [
                        {
                            "name": pkg.name,
                            "version": pkg.version,
                            "source": pkg.source,
                            "path": str(pkg.path),
                        }
                        for pkg in packages
                    ],
                    indent=2,
                ),
            )
        ]

    if name == "validate_package":
        project_path = get_project_root()
        manager = PackageManager(project_path)
        try:
            is_valid = manager.validate(arguments["source"])
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"valid": is_valid},
                        indent=2,
                    ),
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"valid": False, "error": str(e)},
                        indent=2,
                    ),
                )
            ]

    # Project Validation
    if name == "project_validate":
        # Note: ProjectValidator not yet extracted, will be done in future phase
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"error": "ProjectValidator not yet available in UACS"}, indent=2
                ),
            )
        ]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


__all__ = ["server", "main"]
