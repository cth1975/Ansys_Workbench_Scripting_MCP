# Claude Desktop STDIO Setup Guide

This guide shows you how to connect Claude Desktop directly to your Ansys Workbench Scripting MCP Server using STDIO transport, bypassing the MCP Inspector validation bug.

## Quick Setup

### 1. Locate Claude Desktop Configuration File

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `C:\Users\{username}\AppData\Roaming\Claude\claude_desktop_config.json`

### 2. Copy the Configuration

Copy the contents from `claude_desktop_config.json` in this project directory to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "ansys-workbench": {
      "command": "/opt/anaconda3/bin/python",
      "args": ["/Users/christopherhoughton/Dropbox/Code/Ansys_Workbench_Scripting_MCP/server_stdio.py"],
      "env": {
        "PYTHONPATH": "/Users/christopherhoughton/Dropbox/Code/Ansys_Workbench_Scripting_MCP"
      }
    }
  }
}
```

### 3. Adjust Paths for Your System

**Update the paths to match your system:**

- `command`: Update to your Python executable path
  - Check with: `which python` or `which python3`
  - Common paths:
    - `/opt/anaconda3/bin/python` (Anaconda)
    - `/usr/bin/python3` (System Python)
    - `/usr/local/bin/python3` (Homebrew)

- `args`: Update to your project directory path
  - Use the full absolute path to `server_stdio.py`

- `env.PYTHONPATH`: Update to your project directory

### 4. Restart Claude Desktop

After saving the configuration file, restart Claude Desktop completely for the changes to take effect.

## Verification

### Check Connection Status

1. Open Claude Desktop
2. Look for the MCP tools icon (🔧) in the interface
3. You should see your Ansys Workbench server listed

### Test Resources

Try asking Claude:
- "What resources do you have available?"
- "Show me the ansys://workbench/overview resource"
- "Search the Ansys docs for PyMechanical"

### Expected Capabilities

Once connected, Claude will have access to:

- **📄 9 Resources**:
  - `ansys://workbench/overview` - Workbench automation overview
  - `ansys://pymechanical/architecture` - PyMechanical implementation details
  - `ansys://python/cpython-vs-ironpython` - Python implementation comparison
  - `ansys://reference/quick-guide` - Quick reference for common tasks
  - `ansys://act/development` - ACT development guide
  - `ansys://dpf/post-processing` - DPF post-processing reference
  - `ansys://scripting/examples` - Comprehensive scripting examples
  - `ansys://api/reference` - API reference documentation

- **🛠️ 3 Tools**:
  - `search_ansys_docs` - Search across 2000+ pages of documentation
  - `get_code_example` - Find code examples for specific topics
  - `get_chapter_content` - Extract specific chapters from PDF manuals

- **🎯 3 Prompts**:
  - `generate_ansys_script` - Generate automation scripts
  - `debug_ansys_error` - Diagnose and resolve scripting errors
  - `convert_ironpython_to_cpython` - Migrate legacy scripts

## Troubleshooting

### Server Not Connecting

1. **Check file paths**: Ensure all paths in the config are absolute and correct
2. **Verify Python path**: Test that the Python command works from terminal
3. **Check permissions**: Ensure Claude Desktop can access the files
4. **Restart Claude Desktop**: Always restart after config changes

### Testing the Server Manually

You can test the STDIO server directly:

```bash
cd /path/to/your/project
python server_stdio.py
```

The server should start and show initialization messages on stderr. Press Ctrl+C to stop.

### Common Issues

**"Command not found"**: Update the `command` path to the correct Python executable
**"File not found"**: Update the `args` path to the correct server_stdio.py location
**"Module not found"**: Update the `PYTHONPATH` environment variable

### Getting Help

If you encounter issues:
1. Check the Claude Desktop logs (if available)
2. Test the server manually first
3. Verify all paths are absolute and accessible
4. Try the HTTP/SSE version as an alternative

## Why This Works vs. MCP Inspector

- **MCP Inspector**: Has a validation bug in the Python MCP SDK v1.14.0 that causes -32602 errors
- **Claude Desktop**: Uses the production STDIO transport that bypasses this validation issue
- **Result**: Same server, same functionality, but working connection

This approach gives you immediate access to your comprehensive Ansys documentation corpus through Claude Desktop while the SDK bug is being resolved.