# Simple FastMCP Server

A beginner-friendly Model Context Protocol (MCP) server that demonstrates how to create and expose text resources and prompt templates. This is perfect for learning MCP fundamentals!

## What is MCP?

Model Context Protocol (MCP) is a standardized way for AI assistants (like Claude) to access external resources and tools. Think of it as a bridge between AI models and your custom data or functionality.

## What This Server Does

This simple server exposes two types of MCP capabilities:

### 1. Text Resources 📄
Static content that can be retrieved by AI assistants:
- **Company Information**: Basic company details
- **Product Catalog**: List of products and pricing
- **API Documentation**: REST API docs and guidelines

### 2. Prompt Templates 🎯
Reusable prompt templates that accept parameters:
- **analyze_data**: Generate data analysis prompts
- **write_email**: Create professional email templates
- **code_review**: Generate code review checklists

## Quick Start

### Option 1: Super Easy Launch 🚀 (Recommended for Beginners)

Use our automated launcher that starts everything for you:

```bash
# This will automatically start both the MCP server and MCP Inspector
python launcher.py
```

The launcher will:
- ✅ Check and install dependencies automatically
- 🚀 Start your MCP server in the background
- 🌐 Launch MCP Inspector in your browser
- 🔗 Show you exactly how to connect them
- 🧹 Clean up everything when you press Ctrl+C

**That's it!** The launcher handles everything automatically and gives you clear instructions.

### Option 2: Manual Setup

If you prefer to understand each step or want more control:

#### 1. Install Dependencies

First, make sure you have Python 3.8+ and Node.js installed, then:

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Test the Server

Run the server directly to make sure it starts without errors:

```bash
python server.py
```

The server will start and wait for MCP protocol messages. You should see it running (it won't print anything - that's normal!). Press `Ctrl+C` to stop it.

## Testing with MCP Inspector

[MCP Inspector](https://github.com/modelcontextprotocol/inspector) is a web-based tool for testing MCP servers.

### If Using the Launcher 🚀

If you used `python launcher.py`, everything is already set up! Just follow the connection instructions shown in your terminal.

### Manual MCP Inspector Setup

If you're doing manual setup, here's how to connect MCP Inspector to your server:

#### 1. Install MCP Inspector

```bash
# Install globally via npm
npm install -g @modelcontextprotocol/inspector

# Or run directly with npx (no installation needed)
npx @modelcontextprotocol/inspector
```

#### 2. Start the Inspector

```bash
# If installed globally:
mcp-inspector

# Or with npx:
npx @modelcontextprotocol/inspector
```

This will open a web browser with the MCP Inspector interface.

#### 3. Connect to Your Server

**Current Running Setup (Copy & Paste Ready):**

🌐 **MCP Inspector URL:** http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=3c4c9d201c44466984c7bb6950fa75ee1974b9c3576d2a533460dff2e736798a

In the MCP Inspector interface:

1. **Transport Type**: Select "stdio"
2. **Command**:
   ```
   /Users/christopherhoughton/Dropbox/Code/Ansys_Workbench_Scripting_MCP/.venv/bin/python
   ```

3. **Args**:
   ```
   /Users/christopherhoughton/Dropbox/Code/Ansys_Workbench_Scripting_MCP/server.py
   ```

4. **Working Directory**:
   ```
   /Users/christopherhoughton/Dropbox/Code/Ansys_Workbench_Scripting_MCP
   ```

5. Click **"Connect"**

---

**Generic Setup (for other users):**

In the MCP Inspector interface:

1. **Transport Type**: Select "stdio" (this is how our server communicates)
2. **Command**: Enter the full path to your server:
   ```
   python /full/path/to/your/server.py
   ```

   For example:
   ```
   python /Users/yourname/simple-mcp-server/server.py
   ```

3. **Working Directory**: Set to your project directory:
   ```
   /Users/yourname/simple-mcp-server
   ```

4. Click **"Connect"**

#### 4. Explore the Server

Once connected, you can:

#### Test Resources:
1. Go to the **"Resources"** tab
2. You'll see three resources listed:
   - `text://company_info`
   - `text://product_catalog`
   - `text://api_docs`
3. Click on any resource to view its content

#### Test Prompts:
1. Go to the **"Prompts"** tab
2. You'll see three prompts:
   - `analyze_data`
   - `write_email`
   - `code_review`
3. Select a prompt and fill in the parameters
4. Click **"Get Prompt"** to see the generated prompt text

## Understanding the Code

### Server Structure

```python
# 1. Import MCP libraries
from mcp.server import Server
from mcp.server.stdio import stdio_server

# 2. Create server instance
server = Server("simple-fastmcp-server")

# 3. Define handlers with decorators
@server.list_resources()
@server.read_resource()
@server.list_prompts()
@server.get_prompt()

# 4. Run the server
asyncio.run(main())
```

### Key Concepts

- **Resources**: Static content identified by URIs (like `text://company_info`)
- **Prompts**: Template functions that accept parameters and return customized prompts
- **Handlers**: Functions decorated with `@server.decorator()` that respond to MCP requests
- **stdio Transport**: Communication method using standard input/output streams

### Adding Your Own Content

#### Add a New Resource:

1. Add data to the `SAMPLE_DATA` dictionary:
   ```python
   SAMPLE_DATA["my_resource"] = "My custom content here"
   ```

2. Add to the `list_resources()` function:
   ```python
   Resource(
       uri="text://my_resource",
       name="My Resource",
       description="Description of my resource",
       mimeType="text/plain"
   )
   ```

#### Add a New Prompt:

1. Add to `list_prompts()`:
   ```python
   Prompt(
       name="my_prompt",
       description="What my prompt does",
       arguments=[
           PromptArgument(
               name="parameter_name",
               description="What this parameter is for",
               required=True
           )
       ]
   )
   ```

2. Add handling in `get_prompt()`:
   ```python
   elif name == "my_prompt":
       param = arguments.get("parameter_name", "default_value")
       prompt_text = f"Custom prompt using {param}"
   ```

## Troubleshooting

### Common Issues:

1. **"Command not found" in MCP Inspector**
   - Make sure you're using the full absolute path to your server.py file
   - Ensure Python is in your PATH

2. **"Connection failed"**
   - Check that your server runs without errors when started directly
   - Verify all dependencies are installed

3. **"Module not found" errors**
   - Make sure you've activated your virtual environment
   - Run `pip install -r requirements.txt` again

### Debug Mode

To see what's happening, you can add some logging to your server:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

Once you understand this basic server, you can:

1. **Add Tools**: Extend the server to expose callable functions
2. **Connect to Databases**: Read data from real databases instead of static dictionaries
3. **Add Authentication**: Secure your server with API keys or tokens
4. **Deploy**: Run your server in production environments
5. **Integrate**: Connect your server to Claude Desktop or other MCP clients

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Claude Desktop MCP Guide](https://claude.ai/docs/mcp)

Happy MCP building! 🚀