#!/usr/bin/env python3
"""
Standalone MCP Server runner
This runs the MCP server on a TCP socket instead of stdio
"""

import asyncio
import os
from mcp.server import Server
from mcp.server.session import ServerSession
import socket

from server import TaskManagementMCPServer

HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_SERVER_PORT", "9000"))

async def handle_client(reader, writer):
    """Handle a single MCP client connection"""
    print(f"New MCP client connected")
    
    server = TaskManagementMCPServer()
    
    try:
        # Create a session for this client
        session = ServerSession(
            server=server.server,
            reader=reader,
            writer=writer
        )
        
        await session.run()
        
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        await server.cleanup()
        writer.close()
        await writer.wait_closed()
        print("MCP client disconnected")

async def main():
    """Run the MCP server on TCP socket"""
    print(f"Starting MCP server on {HOST}:{PORT}")
    
    server = await asyncio.start_server(
        handle_client,
        HOST,
        PORT
    )
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())