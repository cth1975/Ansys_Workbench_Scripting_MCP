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
    print("  📄 4 Resources:")
    print("    • ansys://workbench/overview - Workbench automation overview")
    print("    • ansys://pymechanical/architecture - PyMechanical implementation details")
    print("    • ansys://python/cpython-vs-ironpython - Python implementation comparison")
    print("    • ansys://reference/quick-guide - Quick reference for common tasks")
    print("")
    print("  🎯 3 Prompts:")
    print("    • generate_ansys_script - Generate automation scripts")
    print("    • debug_ansys_error - Diagnose and resolve scripting errors")
    print("    • convert_ironpython_to_cpython - Migrate legacy scripts")
    print("")
    print("🎯 Purpose: Augment AI assistants with Ansys Workbench scripting knowledge")
    print("📚 Documentation: Based on Ansys 2025 R1 and PyMechanical")
    print("")
    print("Connect MCP Inspector to: http://127.0.0.1:8001/sse")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    # Run with SSE transport (HTTP)
    mcp.run(transport="sse")