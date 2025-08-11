#!/usr/bin/env python3
"""
MCPO Setup Script - Exposes MCP Server through OpenAPI
This script demonstrates how to use MCPO to wrap our MCP server and expose it as an OpenAPI service
"""

import asyncio
import json
import os
import subprocess
import sys
import signal
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import time

class MCPOWrapper:
    """Wrapper class for managing MCPO proxy server"""
    
    def __init__(self, 
                 mcpo_port: int = 8002,
                 backend_url: str = "http://localhost:8001", 
                 api_key: str = "task-management-secret"):
        self.mcpo_port = mcpo_port
        self.backend_url = backend_url
        self.api_key = api_key
        self.mcpo_process: Optional[subprocess.Popen] = None
        self.config_file: Optional[str] = None
    
    def create_config_file(self) -> str:
        """Create MCPO configuration file for our MCP server"""
        config = {
            "mcpServers": {
                "task-management": {
                    "command": "python",
                    "args": ["../mcp-server/mcp_server_stdio.py"],
                    "env": {
                        "BACKEND_API_URL": self.backend_url
                    }
                }
            }
        }
        
        # Create temporary config file
        config_path = "/tmp/mcpo_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.config_file = config_path
        print(f"✓ Created MCPO config: {config_path}")
        print(f"Config contents:\n{json.dumps(config, indent=2)}")
        return config_path
    
    def install_mcpo(self):
        """Install MCPO using pip"""
        try:
            print("🔧 Installing MCPO...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "mcpo"
            ], capture_output=True, text=True, check=True)
            print("✓ MCPO installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install MCPO: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise
    
    def check_mcpo_installed(self) -> bool:
        """Check if MCPO is installed"""
        try:
            result = subprocess.run([
                sys.executable, "-c", "import mcpo"
            ], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def start_mcpo_single(self):
        """Start MCPO with single MCP server"""
        try:
            print(f"🚀 Starting MCPO proxy server on port {self.mcpo_port}...")
            
            # Command to start MCPO with our MCP server
            cmd = [
                sys.executable, "-m", "mcpo",
                "--port", str(self.mcpo_port),
                "--api-key", self.api_key,
                "--host", "0.0.0.0",
                "--",
                sys.executable, "../mcp-server/mcp_server_stdio.py"
            ]
            
            # Set environment for the MCP server
            env = os.environ.copy()
            env["BACKEND_API_URL"] = self.backend_url
            
            print(f"Command: {' '.join(cmd)}")
            print(f"Environment: BACKEND_API_URL={self.backend_url}")
            
            self.mcpo_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            print("✓ MCPO process started")
            print(f"📝 PID: {self.mcpo_process.pid}")
            print(f"🌐 OpenAPI docs: http://localhost:{self.mcpo_port}/docs")
            print(f"🔑 API Key: {self.api_key}")
            
            return self.mcpo_process
            
        except Exception as e:
            print(f"❌ Failed to start MCPO: {e}")
            raise
    
    def start_mcpo_config(self):
        """Start MCPO with configuration file"""
        try:
            config_path = self.create_config_file()
            
            print(f"🚀 Starting MCPO with config file on port {self.mcpo_port}...")
            
            cmd = [
                sys.executable, "-m", "mcpo",
                "--port", str(self.mcpo_port),
                "--api-key", self.api_key,
                "--host", "0.0.0.0",
                "--config", config_path
            ]
            
            print(f"Command: {' '.join(cmd)}")
            
            self.mcpo_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            print("✓ MCPO process started with config")
            print(f"📝 PID: {self.mcpo_process.pid}")
            print(f"🌐 Main docs: http://localhost:{self.mcpo_port}/docs")
            print(f"🌐 Task management: http://localhost:{self.mcpo_port}/task-management/docs")
            print(f"🔑 API Key: {self.api_key}")
            
            return self.mcpo_process
            
        except Exception as e:
            print(f"❌ Failed to start MCPO with config: {e}")
            raise
    
    def monitor_process(self):
        """Monitor MCPO process output"""
        if not self.mcpo_process:
            print("❌ No MCPO process to monitor")
            return
        
        print("📊 Monitoring MCPO process (Ctrl+C to stop)...")
        try:
            while self.mcpo_process.poll() is None:
                line = self.mcpo_process.stdout.readline()
                if line:
                    print(f"MCPO: {line.strip()}")
                else:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping MCPO...")
            self.stop()
    
    def stop(self):
        """Stop MCPO process"""
        if self.mcpo_process:
            print("🛑 Stopping MCPO process...")
            self.mcpo_process.terminate()
            try:
                self.mcpo_process.wait(timeout=5)
                print("✓ MCPO stopped gracefully")
            except subprocess.TimeoutExpired:
                print("⚠️ Force killing MCPO process...")
                self.mcpo_process.kill()
                self.mcpo_process.wait()
                print("✓ MCPO force stopped")
            self.mcpo_process = None
        
        # Cleanup config file
        if self.config_file and os.path.exists(self.config_file):
            os.remove(self.config_file)
            print(f"✓ Cleaned up config file: {self.config_file}")
    
    def test_api(self):
        """Test the MCPO API endpoints"""
        import httpx
        
        base_url = f"http://localhost:{self.mcpo_port}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        print(f"🧪 Testing MCPO API at {base_url}...")
        
        try:
            with httpx.Client() as client:
                # Test health endpoint
                print("1. Testing health endpoint...")
                response = client.get(f"{base_url}/health")
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Response: {response.json()}")
                
                # Test OpenAPI schema
                print("2. Testing OpenAPI schema...")
                response = client.get(f"{base_url}/openapi.json")
                print(f"   Status: {response.status_code}")
                
                # Test MCP tools endpoint (if using config)
                if self.config_file:
                    print("3. Testing task creation through MCPO...")
                    response = client.post(
                        f"{base_url}/task-management/tools/create_task",
                        json={
                            "title": "Test task via MCPO",
                            "description": "Created through MCPO proxy",
                            "priority": "medium"
                        },
                        headers=headers
                    )
                    print(f"   Status: {response.status_code}")
                    if response.status_code < 400:
                        print(f"   Response: {response.json()}")
                else:
                    # Single server mode
                    print("3. Testing task creation through MCPO (single mode)...")
                    response = client.post(
                        f"{base_url}/tools/create_task",
                        json={
                            "title": "Test task via MCPO",
                            "description": "Created through MCPO proxy", 
                            "priority": "medium"
                        },
                        headers=headers
                    )
                    print(f"   Status: {response.status_code}")
                    if response.status_code < 400:
                        print(f"   Response: {response.json()}")
                
        except Exception as e:
            print(f"❌ API test failed: {e}")

def main():
    """Main function to demonstrate MCPO usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCPO Wrapper for Task Management MCP Server")
    parser.add_argument("--port", type=int, default=8002, help="MCPO port")
    parser.add_argument("--backend-url", default="http://localhost:8001", help="Backend API URL")
    parser.add_argument("--api-key", default="task-management-secret", help="API key for MCPO")
    parser.add_argument("--mode", choices=["single", "config"], default="single", 
                        help="Run mode: single server or config file")
    parser.add_argument("--install", action="store_true", help="Install MCPO first")
    parser.add_argument("--test", action="store_true", help="Test the API after starting")
    
    args = parser.parse_args()
    
    wrapper = MCPOWrapper(
        mcpo_port=args.port,
        backend_url=args.backend_url,
        api_key=args.api_key
    )
    
    # Install MCPO if requested or not installed
    if args.install or not wrapper.check_mcpo_installed():
        wrapper.install_mcpo()
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Received shutdown signal...")
        wrapper.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start MCPO
        if args.mode == "config":
            wrapper.start_mcpo_config()
        else:
            wrapper.start_mcpo_single()
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Test API if requested
        if args.test:
            wrapper.test_api()
        
        # Monitor process
        wrapper.monitor_process()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        wrapper.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()