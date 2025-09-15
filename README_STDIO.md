# STDIO Transport Implementation

This branch contains an attempt to create a stdio transport version of the Ansys Workbench Scripting MCP Server.

## Status: ⚠️ KNOWN ISSUE

The stdio transport has a **known bug in the MCP SDK v1.14.0** that causes "Invalid request parameters" errors for the `initialize` method and other requests. This is the same issue we discovered during the initial development phase.

## Files in this Branch

### Working STDIO Implementations (with limitations)
1. **`server_stdio.py`** - FastMCP-based stdio server (affected by SDK bug)
2. **`server_stdio_lowlevel.py`** - Low-level Server class stdio implementation (also affected)
3. **`launcher_stdio.py`** - Launcher for stdio servers with MCP Inspector

### Issue Details

**Error**: `{"jsonrpc":"2.0","id":1,"error":{"code":-32602,"message":"Invalid request parameters","data":""}}`

**Root Cause**: MCP SDK stdio transport has JSON-RPC parameter validation issues that reject valid MCP protocol messages.

**Workaround**: Use the HTTP/SSE transport version instead (`server_http.py`).

## Usage (if SDK is fixed)

If the MCP SDK stdio transport is fixed in a future version:

### Quick Start
```bash
# Run stdio server with launcher
python launcher_stdio.py
```

### Manual Connection
```bash
# Run server directly
python server_stdio_lowlevel.py

# Connect with MCP Inspector:
# - Transport: stdio
# - Command: python server_stdio_lowlevel.py
# - Working Directory: [project path]
```

## Content & Capabilities

Both stdio implementations provide the same comprehensive capabilities as the HTTP version:

- **📄 9 Resources**: All Ansys documentation resources
- **🛠️ 3 Tools**: Search, code examples, chapter extraction
- **🎯 3 Prompts**: Script generation, error debugging, migration
- **📚 40+ MB Documentation**: Complete Ansys corpus access

## Recommendation

**Use the HTTP/SSE version instead**: `server_http.py` with `launcher_http.py`

The HTTP/SSE transport is stable, well-tested, and provides identical functionality without the stdio transport limitations.

## Future Development

This branch is preserved for:
1. **Future MCP SDK updates** that may fix stdio transport
2. **Reference implementation** for stdio transport patterns
3. **Community contributions** to resolve stdio issues

---

*For production use, switch to the main branch with HTTP/SSE transport.*