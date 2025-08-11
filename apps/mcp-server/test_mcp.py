#!/usr/bin/env python3
"""
Test script for the MCP server
This simulates how an MCP client would interact with the server
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the MCP server functionality"""
    
    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_stdio.py"],
        env={"BACKEND_API_URL": "http://localhost:8001"}
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            
            # Initialize the session
            await session.initialize()
            
            print("Connected to MCP Server")
            print("=" * 50)
            
            # List available tools
            print("\n📦 Available Tools:")
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # List available resources
            print("\n📚 Available Resources:")
            resources_response = await session.list_resources()
            for resource in resources_response.resources:
                print(f"  - {resource.uri}: {resource.description}")
            
            # List available prompts
            print("\n💬 Available Prompts:")
            prompts_response = await session.list_prompts()
            for prompt in prompts_response.prompts:
                print(f"  - {prompt.name}: {prompt.description}")
            
            print("\n" + "=" * 50)
            print("Testing Tools:")
            print("=" * 50)
            
            # Test creating a task
            print("\n1. Creating a new task...")
            result = await session.call_tool(
                "create_task",
                {
                    "title": "Test task from MCP",
                    "description": "This task was created via MCP server",
                    "priority": "high"
                }
            )
            if result.content:
                print(result.content[0].text)
            
            # Test searching tasks
            print("\n2. Searching for pending tasks...")
            result = await session.call_tool(
                "search_tasks",
                {"status": "pending", "limit": 5}
            )
            if result.content:
                print(result.content[0].text)
            
            print("\n" + "=" * 50)
            print("Testing Resources:")
            print("=" * 50)
            
            # Test reading resources
            print("\n1. Getting task metrics...")
            metrics = await session.read_resource("task://metrics")
            print(metrics.text if hasattr(metrics, 'text') else metrics)
            
            print("\n2. Getting pending tasks...")
            pending = await session.read_resource("task://pending")
            data = json.loads(pending.text if hasattr(pending, 'text') else pending)
            print(f"Found {data.get('total', 0)} pending tasks")
            
            print("\n" + "=" * 50)
            print("Testing Prompts:")
            print("=" * 50)
            
            # Test getting a prompt
            print("\n1. Getting task prioritization prompt...")
            prompt = await session.get_prompt("task_prioritization", {})
            if prompt.messages:
                print(f"Prompt: {prompt.messages[0].content.text[:200]}...")
            
            print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())