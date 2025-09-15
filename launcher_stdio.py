#!/usr/bin/env python3
"""
MCP STDIO Server + Inspector Launcher

This launcher:
1. Starts the MCP server with STDIO transport
2. Launches MCP Inspector
3. Provides connection instructions for STDIO transport
4. Handles cleanup when done
"""

import subprocess
import sys
import time
from pathlib import Path
import signal
import os

class MCPSTDIOLauncher:
    def __init__(self):
        self.server_process = None
        self.inspector_process = None
        self.project_dir = Path(__file__).parent.absolute()
        self.server_path = self.project_dir / "server_stdio.py"
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
            import fitz  # PyMuPDF
            print("✓ PyMuPDF for PDF processing found")
        except ImportError:
            print("✗ PyMuPDF not found. Installing...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "PyMuPDF"], check=True)
                print("✓ PyMuPDF installed")
            except subprocess.CalledProcessError:
                print("✗ Failed to install PyMuPDF")
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

    def start_stdio_server(self):
        """Start the MCP STDIO server."""
        print("🚀 Starting MCP STDIO Server...")

        try:
            # Use virtual environment python if available
            python_cmd = str(self.venv_python) if self.venv_python.exists() else "python"

            # Start the server process but don't capture stdout/stderr since stdio is used for MCP protocol
            self.server_process = subprocess.Popen(
                [python_cmd, str(self.server_path)],
                cwd=str(self.project_dir)
            )

            # Give it a moment to start
            time.sleep(2)

            # Check if the process is still running
            if self.server_process.poll() is None:
                print(f"✓ MCP STDIO Server started (PID: {self.server_process.pid})")
                return True
            else:
                print("✗ Server failed to start")
                return False

        except Exception as e:
            print(f"✗ Failed to start STDIO server: {e}")
            return False

    def start_inspector(self):
        """Start MCP Inspector."""
        print("🌐 Starting MCP Inspector...")

        try:
            self.inspector_process = subprocess.Popen(
                ["npx", "@modelcontextprotocol/inspector"],
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

                print(f"🌐 MCP Inspector started")
                print(f"   Inspector URL: http://localhost:5173")
                print(f"   ✓ Configure with STDIO transport settings below")

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
        """Print clear instructions for connecting via STDIO."""
        print("\n" + "="*70)
        print("🎉 READY TO CONNECT VIA STDIO!")
        print("="*70)
        print("\n📋 In the MCP Inspector web interface, use these settings:")
        print("\n┌─ STDIO Connection Settings ───────────────────────────────┐")
        print("│                                                           │")
        print("│  Transport Type:   stdio                                  │")
        print(f"│  Command:          python {self.server_path}              │")
        print(f"│  Working Directory: {self.project_dir}                    │")
        print("│                                                           │")
        print("└───────────────────────────────────────────────────────────┘")
        print("\n🔧 Manual Configuration Required:")
        print("   1. Open MCP Inspector at http://localhost:5173")
        print("   2. Select 'stdio' transport type")
        print(f"   3. Enter command: python {self.server_path}")
        print(f"   4. Set working directory: {self.project_dir}")
        print("   5. Click 'Connect' button")
        print("   6. Navigate to 'Resources' or 'Tools' tabs to test")
        print("\n📦 Available resources (9 total):")
        print("   • ansys://workbench/overview - Workbench automation overview")
        print("   • ansys://pymechanical/architecture - PyMechanical implementation details")
        print("   • ansys://python/cpython-vs-ironpython - Python implementation comparison")
        print("   • ansys://reference/quick-guide - Quick reference for common tasks")
        print("   • ansys://act/development - ACT development guide")
        print("   • ansys://dpf/post-processing - DPF post-processing reference")
        print("   • ansys://scripting/examples - Comprehensive scripting examples")
        print("   • ansys://api/reference - API reference documentation")
        print("\n🛠️  Available tools (3 total):")
        print("   • search_ansys_docs - Search across 2000+ pages of documentation")
        print("   • get_code_example - Find code examples for specific topics")
        print("   • get_chapter_content - Extract specific chapters from PDF manuals")
        print("\n🎯 Available prompts (3 total):")
        print("   • generate_ansys_script - Generate automation scripts")
        print("   • debug_ansys_error - Diagnose and resolve scripting errors")
        print("   • convert_ironpython_to_cpython - Migrate legacy scripts")
        print("\n📚 Documentation corpus:")
        print("   • 40+ MB extracted from 2042 pages across 4 Ansys manuals")
        print("   • Full-text search with relevance scoring")
        print("   • Chapter-level access to PDF content")
        print(f"\n🔌 Server running via STDIO transport (PID: {self.server_process.pid})")
        print("\n⚠️  Keep this terminal window open while using MCP Inspector!")
        print("   Press Ctrl+C to stop both services when you're done.")
        print("="*70)

    def cleanup(self):
        """Clean up running processes."""
        print("\n🧹 Cleaning up...")

        if self.server_process:
            print("  Stopping MCP STDIO Server...")
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("  ✓ MCP STDIO Server stopped")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("  ✓ MCP STDIO Server stopped (forced)")

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
        print("🚀 MCP STDIO Server + Inspector Launcher")
        print("="*50)

        # Check dependencies
        if not self.check_dependencies():
            return 1

        # Start the STDIO server
        if not self.start_stdio_server():
            self.cleanup()
            return 1

        # Start the inspector
        if not self.start_inspector():
            self.cleanup()
            return 1

        # Keep running
        try:
            print("\n💡 Both services are now running.")
            print("   Use the STDIO connection settings shown above.")
            print("   Press Ctrl+C to stop both services when you're done.\n")

            # Keep the script running
            while True:
                time.sleep(1)

                # Check if server is still running
                if self.server_process and self.server_process.poll() is not None:
                    print("⚠️  MCP STDIO Server stopped unexpectedly")
                    break

                # Check if inspector is still running
                if self.inspector_process and self.inspector_process.poll() is not None:
                    print("⚠️  MCP Inspector stopped unexpectedly")
                    break

        except KeyboardInterrupt:
            print("\n👋 Shutting down STDIO services...")

        finally:
            self.cleanup()

        return 0


def main():
    """Entry point for the STDIO launcher."""
    launcher = MCPSTDIOLauncher()

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