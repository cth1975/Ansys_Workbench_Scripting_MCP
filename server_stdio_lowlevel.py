#!/usr/bin/env python3
"""
Ansys Workbench Scripting MCP Server - STDIO Transport (Low-Level)

This version uses the low-level Server class to avoid the FastMCP stdio issues.
Provides the same comprehensive Ansys documentation access through stdio.
"""

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import (
    TextContent,
    Resource,
    Tool,
    Prompt,
    GetPromptResult,
    CallToolResult,
    ReadResourceResult,
    ListResourcesResult,
    ListPromptsResult,
    ListToolsResult,
)
from pydantic import AnyUrl
from ansys_resource_loader import get_resource_content, resource_loader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
app = Server("Ansys Workbench Scripting Server (STDIO)")

# Define resources
RESOURCES = [
    Resource(
        uri=AnyUrl("ansys://workbench/overview"),
        name="Ansys Workbench Overview",
        description="Comprehensive overview of Ansys Workbench scripting capabilities",
        mimeType="text/markdown",
    ),
    Resource(
        uri=AnyUrl("ansys://pymechanical/architecture"),
        name="PyMechanical Architecture",
        description="Detailed PyMechanical architecture and implementation details",
        mimeType="text/markdown",
    ),
    Resource(
        uri=AnyUrl("ansys://python/cpython-vs-ironpython"),
        name="CPython vs IronPython Guide",
        description="Comprehensive guide comparing CPython vs IronPython in Ansys context",
        mimeType="text/markdown",
    ),
    Resource(
        uri=AnyUrl("ansys://reference/quick-guide"),
        name="Quick Reference Guide",
        description="Quick reference guide for common Ansys Workbench scripting tasks",
        mimeType="text/markdown",
    ),
    Resource(
        uri=AnyUrl("ansys://act/development"),
        name="ACT Development Guide",
        description="ACT (Application Customization Toolkit) development guide",
        mimeType="text/markdown",
    ),
    Resource(
        uri=AnyUrl("ansys://dpf/post-processing"),
        name="DPF Post-Processing Guide",
        description="DPF post-processing reference and examples",
        mimeType="text/markdown",
    ),
    Resource(
        uri=AnyUrl("ansys://scripting/examples"),
        name="Scripting Examples",
        description="Comprehensive scripting examples from all documentation",
        mimeType="text/markdown",
    ),
    Resource(
        uri=AnyUrl("ansys://api/reference"),
        name="API Reference",
        description="API reference documentation and method signatures",
        mimeType="text/markdown",
    ),
]

# Define tools
TOOLS = [
    Tool(
        name="search_ansys_docs",
        description="Search across all Ansys documentation (PDFs and HTML)",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query terms",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="get_code_example",
        description="Get code examples related to a specific topic",
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic or keyword to find code examples for",
                },
            },
            "required": ["topic"],
        },
    ),
    Tool(
        name="get_chapter_content",
        description="Get content from a specific chapter in an Ansys PDF manual",
        inputSchema={
            "type": "object",
            "properties": {
                "pdf_name": {
                    "type": "string",
                    "description": "Name of the PDF (e.g., 'scripting_mechanical_2025r1.pdf')",
                },
                "chapter_title": {
                    "type": "string",
                    "description": "Title or partial title of the chapter",
                },
            },
            "required": ["pdf_name", "chapter_title"],
        },
    ),
]

# Define prompts
PROMPTS = [
    Prompt(
        name="generate_ansys_script",
        description="Generate Ansys Workbench automation script for a specific task",
        arguments=[
            {
                "name": "task_description",
                "description": "Description of the automation task to accomplish",
                "required": True,
            },
            {
                "name": "ansys_version",
                "description": "Target Ansys version (2024 R1, 2024 R2, 2025 R1, etc.)",
                "required": False,
            },
            {
                "name": "python_type",
                "description": "Python implementation (CPython, IronPython)",
                "required": False,
            },
        ],
    ),
    Prompt(
        name="debug_ansys_error",
        description="Help diagnose and resolve Ansys scripting errors",
        arguments=[
            {
                "name": "error_message",
                "description": "The error message or exception encountered",
                "required": True,
            },
            {
                "name": "context",
                "description": "Additional context about what was being attempted",
                "required": False,
            },
            {
                "name": "ansys_version",
                "description": "Ansys version being used",
                "required": False,
            },
        ],
    ),
    Prompt(
        name="convert_ironpython_to_cpython",
        description="Convert IronPython Ansys scripts to CPython with PyMechanical",
        arguments=[
            {
                "name": "ironpython_code",
                "description": "The IronPython code to convert",
                "required": True,
            },
            {
                "name": "target_features",
                "description": "Specific features to enhance (basic conversion, error handling, modern patterns, etc.)",
                "required": False,
            },
        ],
    ),
]

# Resource handlers
@app.list_resources()
async def list_resources() -> ListResourcesResult:
    """List available resources."""
    return ListResourcesResult(resources=RESOURCES)

@app.read_resource()
async def read_resource(uri: AnyUrl) -> ReadResourceResult:
    """Read a specific resource."""
    uri_str = str(uri)

    # Map URIs to resource content functions
    resource_map = {
        "ansys://workbench/overview": "workbench_overview",
        "ansys://pymechanical/architecture": "pymechanical_architecture",
        "ansys://python/cpython-vs-ironpython": "cpython_vs_ironpython",
        "ansys://reference/quick-guide": "quick_reference",
        "ansys://act/development": "act_development",
        "ansys://dpf/post-processing": "dpf_post_processing",
        "ansys://scripting/examples": "scripting_examples",
        "ansys://api/reference": "api_reference",
    }

    if uri_str in resource_map:
        content = get_resource_content(resource_map[uri_str])
        return ReadResourceResult(
            contents=[TextContent(type="text", text=content)]
        )
    else:
        raise ValueError(f"Unknown resource: {uri}")

# Tool handlers
@app.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(tools=TOOLS)

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Call a specific tool."""

    if name == "search_ansys_docs":
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)

        results = resource_loader.search_content(query, max_results)

        if not results:
            content = f"No results found for query: '{query}'"
        else:
            content = f"# Search Results for: '{query}'\n\n"
            content += f"Found {len(results)} relevant results:\n\n"

            for i, result in enumerate(results, 1):
                content += f"## Result {i}: {result['source']}\n"

                if result['type'] == 'pdf':
                    content += f"**Source**: {result['source']} (Page {result['page']})\n"
                else:
                    content += f"**Source**: {result.get('title', 'Unknown Title')}\n"

                content += f"**Type**: {result['type'].upper()}\n"
                content += f"**Relevance**: {result['relevance_score']:.3f}\n\n"
                content += f"**Context**:\n{result['context']}\n\n"
                content += "---\n\n"

        return CallToolResult(content=[TextContent(type="text", text=content)])

    elif name == "get_code_example":
        topic = arguments.get("topic", "")

        examples = resource_loader.get_code_examples()
        relevant_examples = [ex for ex in examples if topic.lower() in ex.get('code', '').lower() or topic.lower() in ex.get('context', '').lower()]

        if not relevant_examples:
            content = f"No code examples found for topic: '{topic}'"
        else:
            content = f"# Code Examples for: '{topic}'\n\n"

            for i, example in enumerate(relevant_examples[:5], 1):
                content += f"## Example {i}\n"
                content += f"**Source**: {example.get('source', 'Unknown')} (Page {example.get('page', 'N/A')})\n"
                content += f"**Type**: {example.get('type', 'code')}\n\n"
                content += f"```python\n{example.get('code', '')}\n```\n\n"
                if example.get('context'):
                    content += f"**Context**: {example['context'][:300]}...\n\n"
                content += "---\n\n"

        return CallToolResult(content=[TextContent(type="text", text=content)])

    elif name == "get_chapter_content":
        pdf_name = arguments.get("pdf_name", "")
        chapter_title = arguments.get("chapter_title", "")

        chapter_content = resource_loader.get_pdf_content_by_chapter(pdf_name, chapter_title)

        if not chapter_content:
            available_chapters = resource_loader.get_pdf_chapters(pdf_name)
            chapter_list = "\n".join([f"- {ch.get('title', 'Unknown')}" for ch in available_chapters])
            content = f"Chapter '{chapter_title}' not found in {pdf_name}.\n\nAvailable chapters:\n{chapter_list}"
        else:
            content = f"# {chapter_content.get('title', 'Unknown Chapter')}\n\n"
            content += f"**Source**: {pdf_name}\n"
            content += f"**Pages**: {chapter_content.get('start_page', 'N/A')} - {chapter_content.get('end_page', 'N/A')}\n\n"

            chapter_text = chapter_content.get('content', '')
            if len(chapter_text) > 5000:
                content += chapter_text[:5000] + "\n\n*[Content truncated - use search for specific topics]*"
            else:
                content += chapter_text

        return CallToolResult(content=[TextContent(type="text", text=content)])

    else:
        raise ValueError(f"Unknown tool: {name}")

# Prompt handlers
@app.list_prompts()
async def list_prompts() -> ListPromptsResult:
    """List available prompts."""
    return ListPromptsResult(prompts=PROMPTS)

@app.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str]) -> GetPromptResult:
    """Get a specific prompt."""

    if name == "generate_ansys_script":
        task_description = arguments.get("task_description", "")
        ansys_version = arguments.get("ansys_version", "2025 R1")
        python_type = arguments.get("python_type", "CPython")

        framework = "PyMechanical (recommended)" if python_type.lower() == "cpython" else "IronPython scripting"

        content = f"""
Generate an Ansys Workbench automation script for the following task:

**Task**: {task_description}
**Target Version**: {ansys_version}
**Python Framework**: {framework}

Please provide:

1. **Complete Python Script**
   - Proper imports and initialization
   - Error handling and validation
   - Clear comments explaining each step
   - Best practices for {python_type}

2. **Setup Requirements**
   - Required Ansys modules/licenses
   - Python package dependencies
   - Environment setup instructions

3. **Usage Instructions**
   - How to run the script
   - Expected inputs and outputs
   - Troubleshooting common issues

4. **Code Structure**
   - Main automation logic
   - Helper functions if needed
   - Proper resource cleanup

Focus on modern Ansys automation best practices and include comprehensive error handling.
Ensure the script follows Ansys {ansys_version} API patterns and conventions.
"""

        return GetPromptResult(
            description=f"Generate Ansys script for: {task_description}",
            messages=[
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": content
                    }
                }
            ]
        )

    elif name == "debug_ansys_error":
        error_message = arguments.get("error_message", "")
        context = arguments.get("context", "")
        ansys_version = arguments.get("ansys_version", "2025 R1")

        content = f"""
Help diagnose and resolve this Ansys scripting error:

**Error Message**: {error_message}
**Context**: {context}
**Ansys Version**: {ansys_version}

Please provide:

1. **Error Analysis**
   - Likely root cause of the error
   - Common scenarios that trigger this error
   - Whether it's version-specific

2. **Solution Steps**
   - Step-by-step resolution approach
   - Code fixes or workarounds
   - Alternative approaches if needed

3. **Prevention Strategies**
   - Best practices to avoid this error
   - Proper error handling patterns
   - Validation checks to implement

4. **Related Issues**
   - Similar errors and their solutions
   - Known limitations or bugs
   - Version compatibility notes

Include specific code examples and explain the technical reasoning behind the solution.
Focus on both immediate fixes and long-term code improvement strategies.
"""

        return GetPromptResult(
            description=f"Debug Ansys error: {error_message[:50]}...",
            messages=[
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": content
                    }
                }
            ]
        )

    elif name == "convert_ironpython_to_cpython":
        ironpython_code = arguments.get("ironpython_code", "")
        target_features = arguments.get("target_features", "basic conversion")

        content = f"""
Convert the following IronPython Ansys script to modern CPython using PyMechanical:

**Original IronPython Code**:
```python
{ironpython_code}
```

**Target Features**: {target_features}

Please provide:

1. **Converted CPython Script**
   - Modern PyMechanical syntax
   - Proper initialization and setup
   - Enhanced error handling
   - Python 3+ best practices

2. **Key Changes Explained**
   - What changed and why
   - New capabilities enabled
   - Performance improvements

3. **Migration Notes**
   - Dependencies to install
   - Environment setup requirements
   - Testing recommendations

4. **Enhanced Features** (if requested)
   - Better error handling
   - Logging integration
   - Modern Python patterns
   - Package ecosystem integration

Focus on creating maintainable, modern Python code that takes advantage of
the full CPython ecosystem while maintaining compatibility with Ansys automation requirements.
"""

        return GetPromptResult(
            description=f"Convert IronPython to CPython with {target_features}",
            messages=[
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": content
                    }
                }
            ]
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")

async def main():
    """Main server entry point."""
    # Print startup message to stderr (since stdout is used for MCP protocol)
    print("🚀 Starting Ansys Workbench Scripting MCP Server (STDIO Transport)", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("", file=sys.stderr)
    print("🔧 Ansys Workbench Scripting Server Capabilities:", file=sys.stderr)
    print("  📄 9 Resources:", file=sys.stderr)
    print("    • ansys://workbench/overview - Workbench automation overview", file=sys.stderr)
    print("    • ansys://pymechanical/architecture - PyMechanical implementation details", file=sys.stderr)
    print("    • ansys://python/cpython-vs-ironpython - Python implementation comparison", file=sys.stderr)
    print("    • ansys://reference/quick-guide - Quick reference for common tasks", file=sys.stderr)
    print("    • ansys://act/development - ACT development guide", file=sys.stderr)
    print("    • ansys://dpf/post-processing - DPF post-processing reference", file=sys.stderr)
    print("    • ansys://scripting/examples - Comprehensive scripting examples", file=sys.stderr)
    print("    • ansys://api/reference - API reference documentation", file=sys.stderr)
    print("", file=sys.stderr)
    print("  🛠️  3 Tools:", file=sys.stderr)
    print("    • search_ansys_docs - Search across 2000+ pages of documentation", file=sys.stderr)
    print("    • get_code_example - Find code examples for specific topics", file=sys.stderr)
    print("    • get_chapter_content - Extract specific chapters from PDF manuals", file=sys.stderr)
    print("", file=sys.stderr)
    print("  🎯 3 Prompts:", file=sys.stderr)
    print("    • generate_ansys_script - Generate automation scripts", file=sys.stderr)
    print("    • debug_ansys_error - Diagnose and resolve scripting errors", file=sys.stderr)
    print("    • convert_ironpython_to_cpython - Migrate legacy scripts", file=sys.stderr)
    print("", file=sys.stderr)
    print("🎯 Purpose: Augment AI assistants with comprehensive Ansys Workbench scripting knowledge", file=sys.stderr)
    print("📚 Documentation: 40+ MB extracted from 2042 pages across 4 Ansys manuals + HTML docs", file=sys.stderr)
    print("🔍 Search: Full-text search across all documentation with relevance scoring", file=sys.stderr)
    print("", file=sys.stderr)
    print("🔌 Transport: STDIO (for direct MCP client connections)", file=sys.stderr)
    print("📝 Ready for MCP client connections", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    # Run the server
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())