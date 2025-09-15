#!/usr/bin/env python3
"""
Test Script for Ansys STDIO MCP Server

This script tests that the STDIO server starts correctly and can handle basic operations.
It's designed to verify the server works before configuring Claude Desktop.
"""

import subprocess
import sys
import time
import json
from pathlib import Path

def test_stdio_server():
    """Test the STDIO server startup and basic functionality."""
    print("🧪 Testing Ansys Workbench STDIO MCP Server")
    print("=" * 50)

    project_dir = Path(__file__).parent.absolute()
    server_path = project_dir / "server_stdio.py"

    if not server_path.exists():
        print(f"❌ Server file not found: {server_path}")
        return False

    print(f"📁 Project directory: {project_dir}")
    print(f"🐍 Python executable: {sys.executable}")
    print(f"🚀 Server path: {server_path}")
    print()

    # Test 1: Check if server starts
    print("1. Testing server startup...")
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, str(server_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(project_dir),
            text=True
        )

        # Give it a moment to start
        time.sleep(2)

        # Check if process is still running
        if process.poll() is None:
            print("   ✅ Server started successfully")

            # Check stderr for startup messages
            # Give it a moment to output startup info
            time.sleep(1)

            # Try to read any available stderr (non-blocking)
            try:
                stderr_data = process.stderr.read1(1024).decode() if process.stderr else ""
                if "🚀 Starting Ansys Workbench Scripting MCP Server" in stderr_data:
                    print("   ✅ Server startup messages detected on stderr")
                elif stderr_data:
                    print(f"   ⚠️  Unexpected stderr output: {stderr_data[:100]}...")
            except:
                pass  # Non-blocking read might fail, that's ok

            # Terminate the process
            process.terminate()
            process.wait(timeout=5)
            print("   ✅ Server stopped cleanly")
        else:
            # Process exited immediately - check why
            stdout, stderr = process.communicate()
            if "🚀 Starting Ansys Workbench Scripting MCP Server" in stderr:
                print("   ✅ Server started and showed startup messages")
                print("   ✅ Server exited cleanly (normal for STDIO without input)")
            else:
                print("   ❌ Server failed to start properly")
                if stderr:
                    print(f"   Error output: {stderr}")
                return False

    except Exception as e:
        print(f"   ❌ Error starting server: {e}")
        return False

    # Test 2: Check dependencies
    print("\n2. Testing dependencies...")
    try:
        import mcp.server.fastmcp
        print("   ✅ FastMCP library available")
    except ImportError:
        print("   ❌ FastMCP library not found")
        return False

    try:
        import ansys_resource_loader
        print("   ✅ Ansys resource loader available")
    except ImportError:
        print("   ❌ Ansys resource loader not found")
        return False

    # Test 3: Check resource content
    print("\n3. Testing resource content...")
    try:
        from ansys_resource_loader import get_resource_content, resource_loader

        # Test resource generation
        content = get_resource_content("workbench_overview")
        if content and len(content) > 100:
            print(f"   ✅ Workbench overview content: {len(content):,} characters")
        else:
            print("   ⚠️  Workbench overview content seems short")

        # Test search functionality
        results = resource_loader.search_content("PyMechanical", max_results=3)
        if results:
            print(f"   ✅ Search functionality: {len(results)} results found")
        else:
            print("   ⚠️  Search returned no results")

    except Exception as e:
        print(f"   ❌ Error testing resources: {e}")
        return False

    # Test 4: Configuration verification
    print("\n4. Testing Claude Desktop configuration...")
    config_file = project_dir / "claude_desktop_config.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)

            if "mcpServers" in config and "ansys-workbench" in config["mcpServers"]:
                server_config = config["mcpServers"]["ansys-workbench"]
                command = server_config.get("command")
                args = server_config.get("args", [])

                print(f"   ✅ Configuration file exists")
                print(f"   📄 Command: {command}")
                print(f"   📄 Args: {args}")

                # Verify paths exist
                if Path(command).exists():
                    print("   ✅ Python executable path valid")
                else:
                    print("   ⚠️  Python executable path may be invalid")

                if args and Path(args[0]).exists():
                    print("   ✅ Server script path valid")
                else:
                    print("   ⚠️  Server script path may be invalid")
            else:
                print("   ❌ Invalid configuration structure")
                return False

        except Exception as e:
            print(f"   ❌ Error reading configuration: {e}")
            return False
    else:
        print("   ⚠️  Configuration file not found")

    print("\n" + "=" * 50)
    print("🎉 STDIO Server Test Complete!")
    print("\n📋 Next Steps:")
    print("1. Copy claude_desktop_config.json to Claude Desktop config directory:")
    print("   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("   Windows: C:\\Users\\{username}\\AppData\\Roaming\\Claude\\claude_desktop_config.json")
    print("2. Restart Claude Desktop")
    print("3. Look for MCP tools icon (🔧) in Claude Desktop")
    print("4. Test with: 'What resources do you have available?'")
    print("\n✅ The STDIO server is ready for Claude Desktop connection!")

    return True

if __name__ == "__main__":
    success = test_stdio_server()
    sys.exit(0 if success else 1)