# Ansys Workbench Scripting MCP Server

## Real Project Purpose

This MCP server is designed to **augment AI assistants with comprehensive Ansys Workbench scripting knowledge and resources**. The primary focus is on **CPython scripting** for Ansys Workbench automation, addressing the knowledge gap that most AI models have regarding Ansys-specific programming.

### The Problem
- Most AI models lack detailed knowledge about Ansys Workbench Python scripting
- CPython support was recently introduced to Ansys Workbench (alongside existing IronPython)
- Users need assistance writing Python automation scripts for Ansys Workbench
- Limited examples and documentation make it challenging for developers

### The Solution
This MCP server provides AI assistants with:
- Comprehensive Ansys Workbench Python API documentation
- Code templates and patterns for common tasks
- Best practices for CPython vs IronPython differences
- Troubleshooting guides and examples
- Real-world scripting scenarios and solutions

## Project Overview

This project implements a Model Context Protocol (MCP) server that enables AI assistants to access Ansys Workbench scripting resources in a standardized way. Built on a robust HTTP/SSE transport foundation, it will serve as a knowledge bridge for Ansys automation development.

## ✅ SOLUTION IMPLEMENTED

### Issue Resolution
The "Method not found" error has been **RESOLVED** by switching from stdio transport to HTTP/SSE transport. The root cause was identified as a JSON-RPC parameter validation bug in the MCP SDK's stdio transport layer.

## Current Status: INFRASTRUCTURE COMPLETE ✅

The MCP server infrastructure is fully functional with:
- **HTTP/SSE Transport**: Reliable connection to AI assistants via MCP Inspector
- **Auto-configuring launcher** with seamless MCP Inspector integration
- **No manual setup required** - everything pre-configured
- **Ready for Ansys content**: Infrastructure prepared for Ansys-specific resources

### Current Phase: Foundation Complete
- ✅ **MCP Infrastructure**: HTTP/SSE transport working perfectly
- ✅ **Connection Issues Resolved**: Fixed "Method not found" errors
- ✅ **Auto-Configuration**: Seamless launcher and browser integration
- ⏳ **Next Phase**: Replace placeholder resources with Ansys Workbench content

## Development Roadmap

### Phase 1: MCP Infrastructure ✅ COMPLETE
- ✅ Implement working HTTP/SSE transport MCP server
- ✅ Resolve JSON-RPC validation issues with stdio transport
- ✅ Create auto-configuring launcher with MCP Inspector integration
- ✅ Establish GitHub repository with comprehensive documentation

### Phase 2: Resource Gathering 🔄 CURRENT
- 📋 Collect Ansys Workbench Python API documentation
- 📋 Gather CPython-specific examples and patterns
- 📋 Document differences between CPython and IronPython in Ansys context
- 📋 Identify common scripting scenarios and use cases
- 📋 Collect troubleshooting guides and best practices

### Phase 3: Resource Implementation 🔮 NEXT
- 🔮 Replace placeholder resources with Ansys Workbench content
- 🔮 Implement Ansys-specific prompts for code generation
- 🔮 Add code templates for common automation tasks
- 🔮 Create comprehensive API reference resources

### Phase 4: Enhancement & Optimization 🔮 FUTURE
- 🔮 Add interactive code examples and testing
- 🔮 Implement version-specific documentation (different Ansys releases)
- 🔮 Add integration guides for common workflows
- 🔮 Create tutorial sequences for learning paths

## Ansys Resource Categories

### Planned MCP Resources

#### 1. **API Documentation Resources**
- `ansys://api/workbench` - Core Workbench Python API reference
- `ansys://api/mechanical` - Mechanical application scripting
- `ansys://api/fluent` - Fluent automation interfaces
- `ansys://api/cpython-differences` - CPython vs IronPython differences

#### 2. **Code Template Resources**
- `ansys://templates/project-setup` - Project creation and setup patterns
- `ansys://templates/meshing` - Meshing automation templates
- `ansys://templates/analysis` - Analysis setup and execution
- `ansys://templates/post-processing` - Results extraction and reporting

#### 3. **Best Practices Resources**
- `ansys://practices/error-handling` - Robust error handling patterns
- `ansys://practices/performance` - Performance optimization techniques
- `ansys://practices/debugging` - Debugging Ansys Python scripts

#### 4. **Integration Resources**
- `ansys://integration/excel` - Excel integration patterns
- `ansys://integration/external-tools` - Third-party tool connections
- `ansys://integration/batch-processing` - Batch job automation

### Planned MCP Prompts

#### 1. **Code Generation Prompts**
- `generate_ansys_script` - Generate Ansys automation scripts
- `convert_ironpython_cpython` - Convert between Python implementations
- `create_analysis_workflow` - Build complete analysis workflows

#### 2. **Troubleshooting Prompts**
- `debug_ansys_error` - Help diagnose Ansys scripting errors
- `optimize_performance` - Suggest performance improvements
- `review_script` - Code review with Ansys best practices

#### 3. **Learning Prompts**
- `explain_api_usage` - Explain specific API usage patterns
- `tutorial_sequence` - Generate learning tutorials
- `example_walkthrough` - Create detailed code examples

## Project Structure (Clean)

```
Ansys_Workbench_Scripting_MCP/
├── server_http.py        # ✅ Working HTTP/SSE MCP Server
├── launcher_http.py      # ✅ Auto-configuring launcher
├── README.md            # Original project documentation
├── CLAUDE.md            # This documentation
├── DEBUGGING_FINDINGS.md # Research findings (stdio transport bug)
└── .venv/               # Python virtual environment
```

## Environment Details

- **Python**: 3.11.7 (via Anaconda + virtual environment)
- **MCP SDK**: 1.14.0 + FastMCP
- **Transport**: HTTP/SSE (Server-Sent Events)
- **Platform**: macOS Darwin 24.1.0
- **Server Port**: 8001
- **Working Directory**: `/Users/christopherhoughton/Dropbox/Code/Ansys_Workbench_Scripting_MCP`

## How to Use

### Quick Start
```bash
# Run the complete solution (starts server + MCP Inspector)
python launcher_http.py
```

This will:
1. ✅ Start MCP HTTP server on port 8001
2. ✅ Launch MCP Inspector in your browser
3. ✅ Auto-configure connection settings
4. ✅ Pre-select SSE transport and fill in server URL
5. ✅ Display connection instructions

### Manual Server Only
```bash
# Run just the HTTP server
python server_http.py
```

Then connect MCP Inspector manually with:
- **Transport Type**: `sse`
- **Server URL**: `http://127.0.0.1:8001/sse`

## Server Implementation (Final)

The working server uses FastMCP with HTTP/SSE transport:

```python
from mcp.server.fastmcp import FastMCP

# Create MCP server with HTTP settings
mcp = FastMCP(
    "TechCorp Solutions HTTP Server",
    host="127.0.0.1",
    port=8001,
    debug=True
)

# Resources using individual decorators
@mcp.resource("text://company_info")
def get_company_info() -> str:
    return """Company: TechCorp Solutions..."""

# Prompts using individual decorators
@mcp.prompt()
def analyze_data(data_type: str, time_period: str = "monthly") -> str:
    return f"""Analyze {data_type} for {time_period}..."""

# Run with SSE transport
mcp.run(transport="sse")
```

## Root Cause Analysis (Completed)

### ✅ The Problem
- **Issue**: stdio transport had JSON-RPC parameter validation bugs
- **Symptom**: "Method not found" errors despite correct method registration
- **SDK Version**: MCP 1.14.0 has stdio transport issues

### ✅ The Solution
- **Transport**: Switched from stdio to HTTP/SSE
- **Pattern**: Individual decorators (`@mcp.resource()`, `@mcp.prompt()`)
- **Port**: Using 8001 (8000 had conflicts)
- **Auto-config**: Launcher pre-fills MCP Inspector settings

### ✅ Technical Details
The FastMCP handlers were correctly registered:
```python
# These methods existed and worked when called directly:
await mcp.list_prompts()    # ✅ Returned 3 prompts
await mcp.list_resources()  # ✅ Returned 3 resources
```

But stdio transport's JSON-RPC layer rejected `{"method": "prompts/list", "params": {}}` requests with "Invalid request parameters".

HTTP/SSE transport bypasses this validation bug entirely.

## Current Resources (Placeholder Content)

⚠️ **Note**: The current resources are placeholder content from the MCP infrastructure development phase. These will be replaced with Ansys Workbench-specific content in Phase 3.

### Current Placeholder Resources:
1. **Company Info** (`text://company_info`) - *TO BE REPLACED*
   - Currently: TechCorp Solutions information
   - Future: Ansys Workbench overview and capabilities

2. **Product Catalog** (`text://product_catalog`) - *TO BE REPLACED*
   - Currently: Generic product information
   - Future: Ansys application suite and scripting capabilities

3. **API Documentation** (`text://api_docs`) - *TO BE REPLACED*
   - Currently: Generic REST API documentation
   - Future: Ansys Workbench Python API reference

### Current Placeholder Prompts:
1. **analyze_data** - *TO BE REPLACED* with `generate_ansys_script`
2. **write_email** - *TO BE REPLACED* with `convert_ironpython_cpython`
3. **code_review** - *TO BE EVOLVED* to `review_ansys_script`

These placeholders demonstrate the MCP infrastructure works correctly and will serve as templates for implementing the Ansys-specific content.

## Connection Settings

When using MCP Inspector:
```
Transport Type:   sse
Server URL:       http://127.0.0.1:8001/sse
```

The launcher auto-configures these settings, so no manual entry required.

## Dependencies

All dependencies are installed in virtual environment:
- `mcp` - Core MCP SDK
- `fastmcp` - FastMCP framework
- `uvicorn` + `starlette` - HTTP server for SSE transport
- `requests` - HTTP client for launcher health checks

## Testing Verified ✅

- ✅ Server starts successfully on port 8001
- ✅ MCP Inspector connects without errors
- ✅ All 3 resources load and display content
- ✅ All 3 prompts are available and functional
- ✅ Auto-configuration works perfectly
- ✅ No "Method not found" errors

## Development Commands

### Quick Start
```bash
# Complete solution (recommended)
python launcher_http.py

# Server only
python server_http.py

# Check server status
curl http://127.0.0.1:8001/
```

### Development Setup
```bash
# Clone repository from GitHub
git clone https://github.com/cth1975/Ansys_Workbench_Scripting_MCP.git
cd Ansys_Workbench_Scripting_MCP

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### GitHub CLI Commands
```bash
# Check authentication
gh auth status

# Create repository on GitHub
gh repo create Ansys_Workbench_Scripting_MCP --public --description "MCP Server for TechCorp Solutions with HTTP/SSE transport"

# Push to GitHub
git push -u origin main

# View repository
gh repo view --web

# Create issues
gh issue create --title "Feature request" --body "Description"

# Create pull requests (for collaboration)
gh pr create --title "Feature" --body "Description"
```

### Git Workflow
```bash
# Check status
git status

# Stage and commit changes
git add .
git commit -m "Description of changes"

# Push to GitHub
git push

# Pull latest changes (multi-machine setup)
git pull
```

## Multi-Machine Development

This repository includes everything needed for seamless development across multiple machines:

### ✅ Included Files for Development:
- **CLAUDE.md**: Complete project documentation and setup instructions
- **DEBUGGING_FINDINGS.md**: Research findings and technical details
- **requirements.txt & requirements-dev.txt**: All dependencies documented
- **.gitignore**: Proper exclusions configured
- **Working code**: Only production-ready files included

### 🔧 Setting Up on New Machine:
1. **Clone repository**: `git clone https://github.com/cth1975/Ansys_Workbench_Scripting_MCP.git`
2. **Set up virtual environment**: `python -m venv .venv && source .venv/bin/activate`
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run solution**: `python launcher_http.py`
5. **Development ready**: All configuration and documentation included

### 📋 Development Workflow:
- **Make changes**: Edit code as needed
- **Test locally**: `python launcher_http.py`
- **Commit & push**: `git add . && git commit -m "Description" && git push`
- **Pull on other machines**: `git pull` to sync changes

## Project Evolution

### Infrastructure Development (Complete)
1. **Phase 1A**: stdio transport + multiple server implementations → "Method not found" errors
2. **Phase 1B**: Extensive debugging, discovered JSON-RPC validation bug in MCP SDK
3. **Phase 1C**: Implemented HTTP/SSE transport solution → ✅ WORKING
4. **Phase 1D**: Code cleanup, auto-configuration, GitHub deployment → ✅ COMPLETE

### Content Development (Current & Future)
5. **Phase 2A**: Branch creation and project redefinition → ✅ COMPLETE
6. **Phase 2B**: Resource gathering (Ansys documentation, examples) → 🔄 CURRENT
7. **Phase 3A**: Replace placeholder content with Ansys resources → 🔮 NEXT
8. **Phase 3B**: Implement Ansys-specific prompts and templates → 🔮 FUTURE

### Purpose Transition
- **Original Goal**: Demonstrate MCP server functionality with generic content
- **Real Purpose**: Provide comprehensive Ansys Workbench scripting assistance
- **Key Insight**: Strong technical foundation enables focus on Ansys-specific content
- **Current Status**: Infrastructure complete, ready for Ansys content development

## Resources & References

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [FastMCP](https://github.com/jlowin/fastmcp)

---

*Last Updated: 2025-09-14*
*Branch: ansys-resources*
*Status: 🔄 INFRASTRUCTURE COMPLETE - Ready for Ansys content development*
*Current Phase: Resource Gathering (Phase 2B)*
*Next Steps: Collect Ansys Workbench documentation and examples*

### Quick Start for Contributors
```bash
git clone https://github.com/cth1975/Ansys_Workbench_Scripting_MCP.git
cd Ansys_Workbench_Scripting_MCP
git checkout ansys-resources  # Switch to development branch
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python launcher_http.py  # Test infrastructure
```

**Ready to begin Ansys Workbench content development!**