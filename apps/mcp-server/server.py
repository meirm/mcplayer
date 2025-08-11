#!/usr/bin/env python3
"""
MCP Server - Following quick-data-mcp pattern
Provides MCP interface to the backend API
"""

import asyncio
import json
import logging
import os
from typing import Any, Optional
from datetime import datetime

import httpx
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8001")

class TaskManagementMCPServer:
    """
    MCP Server that interfaces with the backend API
    Following the pattern from quick-data-mcp
    """
    
    def __init__(self):
        self.server = Server("task-management-mcp")
        self.http_client = httpx.AsyncClient(base_url=BACKEND_API_URL)
        self._setup_handlers()
        
        # Request context (can be used for auth, session, etc.)
        self.request_context = {}
    
    def _setup_handlers(self):
        """Setup all MCP protocol handlers"""
        
        @self.server.list_resources()
        async def handle_list_resources():
            """List available resources"""
            return [
                Resource(
                    uri="task://list",
                    name="Task List",
                    description="List all tasks with optional filtering",
                    mimeType="application/json",
                ),
                Resource(
                    uri="task://get/{id}",
                    name="Get Task",
                    description="Get a specific task by ID",
                    mimeType="application/json",
                ),
                Resource(
                    uri="analytics://metrics",
                    name="Task Metrics",
                    description="Get task analytics and metrics",
                    mimeType="application/json",
                ),
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str):
            """Read a resource from the backend API"""
            logger.info(f"Reading resource: {uri}")
            
            try:
                if uri.startswith("task://list"):
                    # Fetch task list from backend
                    response = await self.http_client.get("/api/tasks")
                    response.raise_for_status()
                    data = response.json()
                    
                    return TextContent(
                        type="text",
                        text=json.dumps(data, indent=2)
                    )
                
                elif uri.startswith("task://get/"):
                    # Extract task ID from URI
                    task_id = uri.split("/")[-1]
                    response = await self.http_client.get(f"/api/tasks/{task_id}")
                    
                    if response.status_code == 404:
                        return TextContent(
                            type="text",
                            text=json.dumps({"error": "Task not found"})
                        )
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    return TextContent(
                        type="text",
                        text=json.dumps(data, indent=2)
                    )
                
                elif uri == "analytics://metrics":
                    # Fetch analytics from backend
                    response = await self.http_client.get("/api/analytics/metrics")
                    response.raise_for_status()
                    data = response.json()
                    
                    return TextContent(
                        type="text",
                        text=json.dumps(data, indent=2)
                    )
                
                else:
                    return TextContent(
                        type="text",
                        text=json.dumps({"error": f"Unknown resource: {uri}"})
                    )
                    
            except httpx.HTTPError as e:
                logger.error(f"HTTP error reading resource {uri}: {e}")
                return TextContent(
                    type="text",
                    text=json.dumps({"error": f"Failed to fetch resource: {str(e)}"})
                )
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return TextContent(
                    type="text",
                    text=json.dumps({"error": f"Internal error: {str(e)}"})
                )
        
        @self.server.list_tools()
        async def handle_list_tools():
            """List available tools"""
            return [
                Tool(
                    name="create_task",
                    description="Create a new task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Task priority"
                            },
                            "assignee_id": {
                                "type": "integer",
                                "description": "ID of the person assigned to the task"
                            },
                            "due_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Due date for the task"
                            }
                        },
                        "required": ["title"]
                    }
                ),
                Tool(
                    name="update_task",
                    description="Update an existing task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed", "cancelled"],
                                "description": "Task status"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Task priority"
                            },
                            "assignee_id": {
                                "type": "integer",
                                "description": "ID of the person assigned to the task"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="delete_task",
                    description="Delete a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="bulk_update_tasks",
                    description="Update multiple tasks at once",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_ids": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "List of task IDs to update"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed", "cancelled"],
                                "description": "New status for all tasks"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "New priority for all tasks"
                            },
                            "assignee_id": {
                                "type": "integer",
                                "description": "New assignee for all tasks"
                            }
                        },
                        "required": ["task_ids"]
                    }
                ),
                Tool(
                    name="search_tasks",
                    description="Search tasks with filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed", "cancelled"],
                                "description": "Filter by status"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Filter by priority"
                            },
                            "assignee_id": {
                                "type": "integer",
                                "description": "Filter by assignee"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 50
                            }
                        }
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict):
            """Execute a tool by calling the backend API"""
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            
            try:
                if name == "create_task":
                    response = await self.http_client.post(
                        "/api/tasks",
                        json=arguments
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "task": result,
                                "message": f"Task created with ID: {result['id']}"
                            }, indent=2)
                        )
                    ]
                
                elif name == "update_task":
                    task_id = arguments.pop("task_id")
                    response = await self.http_client.put(
                        f"/api/tasks/{task_id}",
                        json=arguments
                    )
                    
                    if response.status_code == 404:
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": False,
                                    "error": "Task not found"
                                })
                            )
                        ]
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "task": result,
                                "message": f"Task {task_id} updated successfully"
                            }, indent=2)
                        )
                    ]
                
                elif name == "delete_task":
                    task_id = arguments["task_id"]
                    response = await self.http_client.delete(f"/api/tasks/{task_id}")
                    
                    if response.status_code == 404:
                        return [
                            TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": False,
                                    "error": "Task not found"
                                })
                            )
                        ]
                    
                    response.raise_for_status()
                    
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "message": f"Task {task_id} deleted successfully"
                            })
                        )
                    ]
                
                elif name == "bulk_update_tasks":
                    task_ids = arguments.pop("task_ids")
                    update_data = {k: v for k, v in arguments.items() if v is not None}
                    
                    response = await self.http_client.post(
                        "/api/tasks/bulk-update",
                        json={
                            "task_ids": task_ids,
                            "update": update_data
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(result, indent=2)
                        )
                    ]
                
                elif name == "search_tasks":
                    # Build query parameters
                    params = {k: v for k, v in arguments.items() if v is not None}
                    
                    response = await self.http_client.get(
                        "/api/tasks",
                        params=params
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(result, indent=2)
                        )
                    ]
                
                else:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "error": f"Unknown tool: {name}"
                            })
                        )
                    ]
                    
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling tool {name}: {e}")
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": f"API error: {str(e)}"
                        })
                    )
                ]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": f"Internal error: {str(e)}"
                        })
                    )
                ]
        
        @self.server.set_logging_level()
        async def handle_set_logging_level(level: LoggingLevel):
            """Set the logging level"""
            logger.info(f"Setting logging level to {level}")
            
            level_map = {
                LoggingLevel.DEBUG: logging.DEBUG,
                LoggingLevel.INFO: logging.INFO,
                LoggingLevel.WARNING: logging.WARNING,
                LoggingLevel.ERROR: logging.ERROR,
            }
            
            logging.getLogger().setLevel(level_map.get(level, logging.INFO))
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting MCP server...")
        
        # Use stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP server running with stdio transport")
            
            initialization_options = InitializationOptions(
                server_name="task-management-mcp",
                server_version="1.0.0",
                capabilities=self.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
            
            await self.server.run(
                read_stream,
                write_stream,
                initialization_options,
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()

async def main():
    """Main entry point"""
    server = TaskManagementMCPServer()
    try:
        await server.run()
    finally:
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())