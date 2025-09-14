#!/usr/bin/env python3
"""
MCP Server with HTTP/SSE Transport
This version uses Server-Sent Events over HTTP instead of stdio
"""

from mcp.server.fastmcp import FastMCP
from ansys_resource_loader import get_resource_content, resource_loader

# Create MCP server instance with HTTP settings
mcp = FastMCP(
    "Ansys Workbench Scripting Server",
    host="127.0.0.1",
    port=8001,
    debug=True
)

# Ansys Workbench Scripting Resources
@mcp.resource("ansys://workbench/overview")
def get_workbench_overview() -> str:
    """Get comprehensive overview of Ansys Workbench scripting capabilities."""
    return get_resource_content("workbench_overview")

@mcp.resource("ansys://pymechanical/architecture")
def get_pymechanical_architecture() -> str:
    """Get detailed PyMechanical architecture and implementation details."""
    return get_resource_content("pymechanical_architecture")

@mcp.resource("ansys://python/cpython-vs-ironpython")
def get_python_comparison() -> str:
    """Get comprehensive guide comparing CPython vs IronPython in Ansys context."""
    return get_resource_content("cpython_vs_ironpython")

@mcp.resource("ansys://reference/quick-guide")
def get_quick_reference() -> str:
    """Get quick reference guide for common Ansys Workbench scripting tasks."""
    return get_resource_content("quick_reference")

@mcp.resource("ansys://act/development")
def get_act_development() -> str:
    """Get ACT (Application Customization Toolkit) development guide."""
    return get_resource_content("act_development")

@mcp.resource("ansys://dpf/post-processing")
def get_dpf_post_processing() -> str:
    """Get DPF post-processing reference and examples."""
    return get_resource_content("dpf_post_processing")

@mcp.resource("ansys://scripting/examples")
def get_scripting_examples() -> str:
    """Get comprehensive scripting examples from all documentation."""
    return get_resource_content("scripting_examples")

@mcp.resource("ansys://api/reference")
def get_api_reference() -> str:
    """Get API reference documentation and method signatures."""
    return get_resource_content("api_reference")

# Ansys-Specific Tools
@mcp.tool()
def search_ansys_docs(query: str, max_results: int = 10) -> str:
    """
    Search across all Ansys documentation (PDFs and HTML).

    Args:
        query: Search query terms
        max_results: Maximum number of results to return (default: 10)
    """
    from ansys_resource_loader import resource_loader

    results = resource_loader.search_content(query, max_results)

    if not results:
        return f"No results found for query: '{query}'"

    search_output = f"# Search Results for: '{query}'\n\n"
    search_output += f"Found {len(results)} relevant results:\n\n"

    for i, result in enumerate(results, 1):
        search_output += f"## Result {i}: {result['source']}\n"

        if result['type'] == 'pdf':
            search_output += f"**Source**: {result['source']} (Page {result['page']})\n"
        else:
            search_output += f"**Source**: {result.get('title', 'Unknown Title')}\n"

        search_output += f"**Type**: {result['type'].upper()}\n"
        search_output += f"**Relevance**: {result['relevance_score']:.3f}\n\n"
        search_output += f"**Context**:\n{result['context']}\n\n"
        search_output += "---\n\n"

    return search_output

@mcp.tool()
def get_code_example(topic: str) -> str:
    """
    Get code examples related to a specific topic.

    Args:
        topic: Topic or keyword to find code examples for
    """
    from ansys_resource_loader import resource_loader

    examples = resource_loader.get_code_examples()
    relevant_examples = [ex for ex in examples if topic.lower() in ex.get('code', '').lower() or topic.lower() in ex.get('context', '').lower()]

    if not relevant_examples:
        return f"No code examples found for topic: '{topic}'"

    output = f"# Code Examples for: '{topic}'\n\n"

    for i, example in enumerate(relevant_examples[:5], 1):  # Limit to 5 examples
        output += f"## Example {i}\n"
        output += f"**Source**: {example.get('source', 'Unknown')} (Page {example.get('page', 'N/A')})\n"
        output += f"**Type**: {example.get('type', 'code')}\n\n"
        output += f"```python\n{example.get('code', '')}\n```\n\n"
        if example.get('context'):
            output += f"**Context**: {example['context'][:300]}...\n\n"
        output += "---\n\n"

    return output

@mcp.tool()
def get_chapter_content(pdf_name: str, chapter_title: str) -> str:
    """
    Get content from a specific chapter in an Ansys PDF manual.

    Args:
        pdf_name: Name of the PDF (e.g., 'scripting_mechanical_2025r1.pdf')
        chapter_title: Title or partial title of the chapter
    """
    from ansys_resource_loader import resource_loader

    chapter_content = resource_loader.get_pdf_content_by_chapter(pdf_name, chapter_title)

    if not chapter_content:
        available_chapters = resource_loader.get_pdf_chapters(pdf_name)
        chapter_list = "\n".join([f"- {ch.get('title', 'Unknown')}" for ch in available_chapters])
        return f"Chapter '{chapter_title}' not found in {pdf_name}.\n\nAvailable chapters:\n{chapter_list}"

    output = f"# {chapter_content.get('title', 'Unknown Chapter')}\n\n"
    output += f"**Source**: {pdf_name}\n"
    output += f"**Pages**: {chapter_content.get('start_page', 'N/A')} - {chapter_content.get('end_page', 'N/A')}\n\n"

    content = chapter_content.get('content', '')
    if len(content) > 5000:  # Truncate very long content
        output += content[:5000] + "\n\n*[Content truncated - use search for specific topics]*"
    else:
        output += content

    return output

# Ansys-Specific Prompts
@mcp.prompt()
def generate_ansys_script(task_description: str, ansys_version: str = "2025 R1", python_type: str = "CPython") -> str:
    """
    Generate Ansys Workbench automation script for a specific task.

    Args:
        task_description: Description of the automation task to accomplish
        ansys_version: Target Ansys version (2024 R1, 2024 R2, 2025 R1, etc.)
        python_type: Python implementation (CPython, IronPython)
    """
    framework = "PyMechanical (recommended)" if python_type.lower() == "cpython" else "IronPython scripting"

    return f"""
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

@mcp.prompt()
def debug_ansys_error(error_message: str, context: str = "", ansys_version: str = "2025 R1") -> str:
    """
    Help diagnose and resolve Ansys scripting errors.

    Args:
        error_message: The error message or exception encountered
        context: Additional context about what was being attempted
        ansys_version: Ansys version being used
    """
    return f"""
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

@mcp.prompt()
def convert_ironpython_to_cpython(ironpython_code: str, target_features: str = "basic conversion") -> str:
    """
    Convert IronPython Ansys scripts to CPython with PyMechanical.

    Args:
        ironpython_code: The IronPython code to convert
        target_features: Specific features to enhance (basic conversion, error handling, modern patterns, etc.)
    """
    return f"""
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

# Run the server with SSE transport
if __name__ == "__main__":
    print("🚀 Starting Ansys Workbench Scripting MCP Server")
    print("=" * 60)
    print(f"Server URL: http://127.0.0.1:8001")
    print(f"SSE Endpoint: http://127.0.0.1:8001/sse")
    print("")
    print("🔧 Ansys Workbench Scripting Server Capabilities:")
    print("  📄 9 Resources:")
    print("    • ansys://workbench/overview - Workbench automation overview")
    print("    • ansys://pymechanical/architecture - PyMechanical implementation details")
    print("    • ansys://python/cpython-vs-ironpython - Python implementation comparison")
    print("    • ansys://reference/quick-guide - Quick reference for common tasks")
    print("    • ansys://act/development - ACT development guide")
    print("    • ansys://dpf/post-processing - DPF post-processing reference")
    print("    • ansys://scripting/examples - Comprehensive scripting examples")
    print("    • ansys://api/reference - API reference documentation")
    print("")
    print("  🛠️  3 Tools:")
    print("    • search_ansys_docs - Search across 2000+ pages of documentation")
    print("    • get_code_example - Find code examples for specific topics")
    print("    • get_chapter_content - Extract specific chapters from PDF manuals")
    print("")
    print("  🎯 3 Prompts:")
    print("    • generate_ansys_script - Generate automation scripts")
    print("    • debug_ansys_error - Diagnose and resolve scripting errors")
    print("    • convert_ironpython_to_cpython - Migrate legacy scripts")
    print("")
    print("🎯 Purpose: Augment AI assistants with comprehensive Ansys Workbench scripting knowledge")
    print("📚 Documentation: 40+ MB extracted from 2042 pages across 4 Ansys manuals + HTML docs")
    print("🔍 Search: Full-text search across all documentation with relevance scoring")
    print("")
    print("Connect MCP Inspector to: http://127.0.0.1:8001/sse")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    # Run with SSE transport (HTTP)
    mcp.run(transport="sse")