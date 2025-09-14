# MCP Server Debugging Findings

## Executive Summary

After extensive debugging, we've discovered that **the FastMCP server IS working correctly**. The handlers are registered, the methods exist, and can be called directly. The issue appears to be in the JSON-RPC message handling layer between the client (MCP Inspector) and the server.

## Key Discoveries

### 1. ✅ Handlers ARE Registered

Testing shows that FastMCP properly registers all handlers:
- `ListPromptsRequest` → Handler exists ✓
- `ListResourcesRequest` → Handler exists ✓
- `GetPromptRequest` → Handler exists ✓
- `ReadResourceRequest` → Handler exists ✓

### 2. ✅ Methods Work When Called Directly

```python
# This works perfectly:
prompts = await mcp.list_prompts()  # Returns 3 prompts
resources = await mcp.list_resources()  # Returns 3 resources
```

### 3. ❌ JSON-RPC Layer Fails

When sending `{"method": "prompts/list", "params": {}}`:
- Error: "Invalid request parameters"
- The handler exists but the JSON-RPC layer rejects the request

## Root Cause Analysis

The issue is in the JSON-RPC request validation layer. The FastMCP/MCP SDK expects:

1. **ListPromptsRequest** accepts:
   - `params: None` (works)
   - `params: {}` (should work, creates PaginatedRequestParams)

2. But something in the validation chain is rejecting empty `{}` params

## Test Results

### Handler Registration Test
```
✓ Has _mcp_server
✓ Has 8 request handlers
✓ ListPromptsRequest handler registered
✓ list_prompts() method works
```

### Direct Method Call Test
```
✓ list_prompts() returned 3 prompts
✓ list_resources() returned 3 resources
```

### JSON-RPC Test
```
✓ Initialize: SUCCESS
✗ prompts/list with {}: FAILED - Invalid request parameters
✗ prompts/list with null: FAILED - Invalid request parameters
```

## The Mystery

Why does the validation fail when:
1. The handler exists
2. The method works directly
3. The request type accepts the parameters

This suggests a bug or version mismatch in:
- The MCP SDK's JSON-RPC validation layer
- The parameter deserialization process
- The request routing mechanism

## Workarounds Attempted

1. **Different parameter formats**: `{}`, `null`, omitted - all fail
2. **Different transports**: stdio, SSE - same issue
3. **Different server patterns**: FastMCP, low-level Server - same issue

## Conclusion

The server implementation is correct. The issue is in the MCP SDK's JSON-RPC request handling, specifically in how it validates or deserializes the `params` field for list methods.

## Next Steps

1. **File a bug report** with the MCP SDK repository
2. **Try older MCP SDK versions** to see if this is a regression
3. **Use HTTP/REST endpoints** instead of JSON-RPC if available
4. **Wait for MCP SDK fix** or clarification from maintainers

---

*Investigation Date: 2025-09-14*
*MCP SDK Version: 1.14.0*
*Python Version: 3.11.7*