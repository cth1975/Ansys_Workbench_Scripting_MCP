#!/usr/bin/env python3
"""
MCP HTTP Server + Inspector Launcher

This launcher:
1. Starts the MCP server with HTTP/SSE transport
2. Launches MCP Inspector
3. Provides connection instructions for HTTP transport
4. Handles cleanup when done
"""

import subprocess
import sys
import time
from pathlib import Path
import signal
import requests


class MCPHTTPLauncher:
    def __init__(self):
        self.server_process = None
        self.inspector_process = None
        self.project_dir = Path(__file__).parent.absolute()
        self.server_path = self.project_dir / "server_http.py"
        self.server_url = "http://127.0.0.1:8001"
        self.sse_url = "http://127.0.0.1:8001/sse"
        self.venv_python = self.project_dir / ".venv" / "bin" / "python"

    def check_dependencies(self):
        """Check if required dependencies are installed."""
        print("🔍 Checking dependencies...")

        # Check Python dependencies
        try:
            import mcp.server.fastmcp
            print("✓ MCP FastMCP library found")
        except ImportError:
            print("✗ MCP FastMCP library not found")
            return False

        try:
            import uvicorn
            import starlette
            print("✓ HTTP server dependencies found")
        except ImportError:
            print("✗ HTTP server dependencies missing. Installing...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "uvicorn", "starlette"], check=True)
                print("✓ HTTP server dependencies installed")
            except subprocess.CalledProcessError:
                print("✗ Failed to install HTTP server dependencies")
                return False

        # Check Node.js/npm for MCP Inspector
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ npm found (version {result.stdout.strip()})")
            else:
                raise subprocess.CalledProcessError(1, "npm")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ npm not found. Please install Node.js to use MCP Inspector")
            print("  You can download it from: https://nodejs.org/")
            return False

        return True

    def start_http_server(self):
        """Start the MCP HTTP server."""
        print("🚀 Starting MCP HTTP Server...")

        try:
            # Use virtual environment python if available
            python_cmd = str(self.venv_python) if self.venv_python.exists() else "python"

            self.server_process = subprocess.Popen(
                [python_cmd, str(self.server_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.project_dir)
            )

            # Wait for server to start
            print("⏳ Waiting for HTTP server to start...")

            # Test server availability
            for attempt in range(10):  # Try for 10 seconds
                try:
                    response = requests.get(f"{self.server_url}/", timeout=1)
                    if response.status_code in [200, 404]:  # Server is responding
                        break
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    continue
            else:
                print("✗ Server failed to start (timeout)")
                return False

            print(f"✓ MCP HTTP Server started at {self.server_url}")
            return True

        except Exception as e:
            print(f"✗ Failed to start HTTP server: {e}")
            return False

    def start_inspector(self):
        """Start MCP Inspector."""
        print("🌐 Starting MCP Inspector...")

        try:
            self.inspector_process = subprocess.Popen(
                ["npx", "@modelcontextprotocol/inspector", "--transport", "sse", "--server-url", self.sse_url],
                cwd=str(self.project_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Give it time to start
            print("⏳ Waiting for MCP Inspector to initialize...")
            time.sleep(5)

            # Check if the process is still running
            if self.inspector_process.poll() is None:
                print("✓ MCP Inspector started successfully")

                # Wait a bit more for the web server to be ready
                print("⏳ Waiting for web interface to be ready...")
                time.sleep(3)

                # MCP Inspector will open automatically with pre-configured settings
                print(f"🌐 MCP Inspector started with SSE transport pre-configured")
                print(f"   Server URL: {self.sse_url}")
                print(f"   Inspector URL: http://localhost:5173")
                print(f"   ✓ Settings auto-configured - should connect automatically!")

                self.print_connection_instructions()
                return True
            else:
                print("✗ MCP Inspector failed to start")
                stderr_output = self.inspector_process.stderr.read().decode() if self.inspector_process.stderr else "No error output"
                print(f"Error output: {stderr_output}")
                return False

        except Exception as e:
            print(f"✗ Failed to start MCP Inspector: {e}")
            return False

    def print_connection_instructions(self):
        """Print clear instructions for connecting via HTTP."""
        print("\n" + "="*70)
        print("🎉 READY TO CONNECT VIA HTTP!")
        print("="*70)
        print("\n📋 In the MCP Inspector web interface, use these settings:")
        print("\n┌─ HTTP Connection Settings ────────────────────────────────┐")
        print("│                                                           │")
        print("│  Transport Type:   sse                                    │")
        print(f"│  Server URL:       {self.sse_url}                         │")
        print("│                                                           │")
        print("└───────────────────────────────────────────────────────────┘")
        print("\n🔧 Connection is fully automatic:")
        print("   ✓ Transport Type: SSE (pre-configured)")
        print(f"   ✓ Server URL: {self.sse_url} (pre-configured)")
        print("   ✓ Should connect automatically on startup")
        print("   → If not connected, click 'Connect' button")
        print("   → Navigate to 'Resources' or 'Prompts' tabs to test")
        print("\n📦 Available resources:")
        print("   • Company Info (text://company_info)")
        print("   • Product Catalog (text://product_catalog)")
        print("   • API Documentation (text://api_docs)")
        print("\n🎯 Available prompts:")
        print("   • analyze_data - Business data analysis")
        print("   • write_email - Professional email templates")
        print("   • code_review - Code review checklists")
        print(f"\n🌐 Server running at: {self.server_url}")
        print(f"📡 SSE endpoint at: {self.sse_url}")
        print("\n⚠️  Keep this terminal window open while using MCP Inspector!")
        print("   Press Ctrl+C to stop both services when you're done.")
        print("="*70)

    def cleanup(self):
        """Clean up running processes."""
        print("\n🧹 Cleaning up...")

        if self.server_process:
            print("  Stopping MCP HTTP Server...")
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("  ✓ MCP HTTP Server stopped")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("  ✓ MCP HTTP Server stopped (forced)")

        if self.inspector_process:
            print("  Stopping MCP Inspector...")
            try:
                self.inspector_process.terminate()
                self.inspector_process.wait(timeout=5)
                print("  ✓ MCP Inspector stopped")
            except subprocess.TimeoutExpired:
                self.inspector_process.kill()
                print("  ✓ MCP Inspector stopped (forced)")

    def run(self):
        """Main launcher logic."""
        print("🚀 MCP HTTP Server + Inspector Launcher")
        print("="*50)

        # Check dependencies
        if not self.check_dependencies():
            return 1

        # Start the HTTP server
        if not self.start_http_server():
            self.cleanup()
            return 1

        # Start the inspector
        if not self.start_inspector():
            self.cleanup()
            return 1

        # Keep running
        try:
            print("\n💡 Both services are now running.")
            print("   Use the HTTP connection settings shown above.")
            print("   Press Ctrl+C to stop both services when you're done.\n")

            # Keep the script running
            while True:
                time.sleep(1)

                # Check if server is still running
                if self.server_process and self.server_process.poll() is not None:
                    print("⚠️  MCP HTTP Server stopped unexpectedly")
                    break

                # Check if inspector is still running
                if self.inspector_process and self.inspector_process.poll() is not None:
                    print("⚠️  MCP Inspector stopped unexpectedly")
                    break

        except KeyboardInterrupt:
            print("\n👋 Shutting down HTTP services...")

        finally:
            self.cleanup()

        return 0


def main():
    """Entry point for the HTTP launcher."""
    launcher = MCPHTTPLauncher()

    # Set up signal handlers for clean shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Received shutdown signal...")
        launcher.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

    return launcher.run()


if __name__ == "__main__":
    sys.exit(main())