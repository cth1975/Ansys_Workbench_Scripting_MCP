# MCP Server Development - Project Documentation

## Project Overview

This project implements a Model Context Protocol (MCP) server for TechCorp Solutions, demonstrating resources and prompts functionality. The MCP allows AI assistants to access external resources and tools in a standardized way.

## ✅ SOLUTION IMPLEMENTED

### Issue Resolution
The "Method not found" error has been **RESOLVED** by switching from stdio transport to HTTP/SSE transport. The root cause was identified as a JSON-RPC parameter validation bug in the MCP SDK's stdio transport layer.

## Current Status: WORKING ✅

The MCP server is now fully functional with:
- **3 Resources**: Company Info, Product Catalog, API Documentation
- **3 Prompts**: Data Analysis, Email Templates, Code Review
- **Auto-configuring launcher** with MCP Inspector integration
- **No manual setup required** - everything pre-configured

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

## Available Resources

1. **Company Info** (`text://company_info`)
   - TechCorp Solutions basic information
   - Founded 2020, 150 employees, San Francisco HQ

2. **Product Catalog** (`text://product_catalog`)
   - 4 products: CloudSync Pro, DataViz Analytics, SecureVault, WorkFlow Manager
   - Pricing: $79-149/month

3. **API Documentation** (`text://api_docs`)
   - REST API endpoints and authentication
   - Rate limits and usage guidelines

## Available Prompts

1. **analyze_data** - Business data analysis with customizable parameters
2. **write_email** - Professional email templates for various recipients
3. **code_review** - Code review checklists for different languages/projects

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

```bash
# Complete solution (recommended)
python launcher_http.py

# Server only
python server_http.py

# Check server status
curl http://127.0.0.1:8001/

# Install dependencies
pip install -r requirements.txt

# Virtual environment
source .venv/bin/activate
```

## Project Evolution

1. **Phase 1**: stdio transport + multiple server implementations → "Method not found" errors
2. **Phase 2**: Extensive debugging, discovered JSON-RPC validation bug in MCP SDK
3. **Phase 3**: Implemented HTTP/SSE transport solution → ✅ WORKING
4. **Phase 4**: Code cleanup, removed obsolete files, auto-configuration → ✅ COMPLETE

## Resources & References

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [FastMCP](https://github.com/jlowin/fastmcp)

---

*Last Updated: 2025-09-14*
*Status: ✅ COMPLETE - HTTP/SSE solution working perfectly*
*Next Steps: Ready for production use*