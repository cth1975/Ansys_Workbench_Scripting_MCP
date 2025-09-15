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

## Debugging Notes

### STDIO Logging Requirements ✅ IMPLEMENTED

The MCP STDIO transport requires:
- **stdout**: Reserved exclusively for JSON-RPC protocol messages
- **stderr**: Used for all diagnostic output, logging, and debugging

**Status**: ✅ **Our implementations correctly follow this requirement**

Both `server_stdio.py` and `server_stdio_lowlevel.py` properly use `file=sys.stderr` for all print statements:

```python
print("🚀 Starting Ansys Workbench Scripting MCP Server (STDIO Transport)", file=sys.stderr)
# All 60+ print statements correctly use file=sys.stderr
```

### Troubleshooting Checklist

- ✅ **Stderr Logging**: Confirmed all diagnostic output goes to stderr
- ✅ **Stdout Reserved**: JSON-RPC protocol uses stdout exclusively
- ✅ **FastMCP Implementation**: Uses proper transport configuration
- ✅ **Low-level Implementation**: Follows MCP Server class patterns
- ❌ **SDK Bug**: Issue persists in MCP SDK v1.14.0 validation layer

### Technical Analysis

The "Invalid request parameters" error occurs during the `initialize` method call, indicating the issue is in the MCP SDK's JSON-RPC parameter validation logic, not in our logging approach or protocol implementation.

**Evidence**:
- Both implementations produce identical errors despite different architectures
- HTTP/SSE transport works with identical handlers and data
- Error occurs before our handlers are invoked
- Proper stderr usage confirmed via code analysis

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

## Working Solution: Claude Desktop Direct Connection

**✅ BYPASS THE INSPECTOR BUG**: Connect Claude Desktop directly to the STDIO server

While MCP Inspector has validation issues, **Claude Desktop uses production STDIO transport that works**.

### Quick Setup

1. **Run the test script** to verify everything works:
   ```bash
   python test_stdio_server.py
   ```

2. **Copy the configuration** to Claude Desktop:
   - **macOS**: Copy `claude_desktop_config.json` to `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: Copy to `C:\Users\{username}\AppData\Roaming\Claude\claude_desktop_config.json`

3. **Restart Claude Desktop** and look for the MCP tools icon (🔧)

4. **Test with Claude**: Ask "What resources do you have available?"

### Detailed Instructions

See `CLAUDE_DESKTOP_SETUP.md` for complete step-by-step instructions.

## Alternative: HTTP/SSE Version

**Use the HTTP/SSE version instead**: `server_http.py` with `launcher_http.py`

The HTTP/SSE transport is stable, well-tested, and provides identical functionality without any transport limitations.

## Future Development

This branch is preserved for:
1. **Future MCP SDK updates** that may fix stdio transport
2. **Reference implementation** for stdio transport patterns
3. **Community contributions** to resolve stdio issues

---

*For production use, switch to the main branch with HTTP/SSE transport.*