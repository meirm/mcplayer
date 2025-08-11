#!/usr/bin/env python3
"""
MCP Server - Standard I/O Implementation
Provides MCP interface to the backend API via stdio transport
"""

import asyncio
import json
import logging
import os
from typing import Any, Optional, Dict, List
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel import NotificationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Backend API configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8001")

class TaskManagementMCPServer:
    """
    MCP Server that interfaces with the backend API
    Provides tools, resources, and prompts for task management
    """
    
    def __init__(self):
        self.server = Server("task-management-mcp")
        self.http_client = httpx.AsyncClient(base_url=BACKEND_API_URL, timeout=30.0)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup all MCP protocol handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="create_task",
                    description="Create a new task in the task management system",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title (required)",
                                "minLength": 1,
                                "maxLength": 200
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description (optional)",
                                "maxLength": 1000
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Task priority level",
                                "default": "medium"
                            },
                            "assignee_id": {
                                "type": "integer",
                                "description": "ID of the person assigned to the task"
                            },
                            "due_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Due date for the task (ISO format)"
                            }
                        },
                        "required": ["title"]
                    }
                ),
                types.Tool(
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
                                "description": "New task title",
                                "minLength": 1,
                                "maxLength": 200
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description",
                                "maxLength": 1000
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
                            },
                            "due_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Due date for the task (ISO format)"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="delete_task",
                    description="Delete a task from the system",
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
                types.Tool(
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
                types.Tool(
                    name="search_tasks",
                    description="Search and filter tasks",
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
                                "default": 50,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Number of results to skip",
                                "default": 0,
                                "minimum": 0
                            }
                        }
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Execute a tool by calling the backend API"""
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            
            try:
                if name == "create_task":
                    response = await self.http_client.post("/api/tasks", json=arguments)
                    response.raise_for_status()
                    result = response.json()
                    
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "task": result,
                                "message": f"Task created successfully with ID: {result['id']}"
                            }, indent=2)
                        )
                    ]
                
                elif name == "update_task":
                    task_id = arguments.pop("task_id")
                    response = await self.http_client.put(f"/api/tasks/{task_id}", json=arguments)
                    
                    if response.status_code == 404:
                        return [
                            types.TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": False,
                                    "error": f"Task {task_id} not found"
                                }, indent=2)
                            )
                        ]
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    return [
                        types.TextContent(
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
                            types.TextContent(
                                type="text",
                                text=json.dumps({
                                    "success": False,
                                    "error": f"Task {task_id} not found"
                                }, indent=2)
                            )
                        ]
                    
                    response.raise_for_status()
                    
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "message": f"Task {task_id} deleted successfully"
                            }, indent=2)
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
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "result": result,
                                "message": f"Updated {result['succeeded']} out of {result['total']} tasks"
                            }, indent=2)
                        )
                    ]
                
                elif name == "search_tasks":
                    # Build query parameters
                    params = {k: v for k, v in arguments.items() if v is not None}
                    
                    response = await self.http_client.get("/api/tasks", params=params)
                    response.raise_for_status()
                    result = response.json()
                    
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "success": True,
                                "tasks": result["tasks"],
                                "total": result["total"],
                                "pagination": {
                                    "limit": result["limit"],
                                    "offset": result["offset"],
                                    "has_more": result["has_more"]
                                }
                            }, indent=2)
                        )
                    ]
                
                else:
                    return [
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "error": f"Unknown tool: {name}"
                            }, indent=2)
                        )
                    ]
                    
            except httpx.HTTPError as e:
                logger.error(f"HTTP error calling tool {name}: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": f"API error: {str(e)}"
                        }, indent=2)
                    )
                ]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": f"Internal error: {str(e)}"
                        }, indent=2)
                    )
                ]
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List available resources"""
            return [
                types.Resource(
                    uri="task://list",
                    name="Task List",
                    description="Get a list of all tasks with optional filtering",
                    mimeType="application/json",
                ),
                types.Resource(
                    uri="task://get/{id}",
                    name="Get Task",
                    description="Get a specific task by its ID",
                    mimeType="application/json",
                ),
                types.Resource(
                    uri="task://metrics",
                    name="Task Metrics",
                    description="Get analytics and metrics about tasks",
                    mimeType="application/json",
                ),
                types.Resource(
                    uri="task://pending",
                    name="Pending Tasks",
                    description="Get all pending tasks",
                    mimeType="application/json",
                ),
                types.Resource(
                    uri="task://completed",
                    name="Completed Tasks",
                    description="Get all completed tasks",
                    mimeType="application/json",
                ),
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a resource from the backend API"""
            logger.info(f"Reading resource: {uri}")
            
            try:
                if uri == "task://list":
                    response = await self.http_client.get("/api/tasks")
                    response.raise_for_status()
                    return json.dumps(response.json(), indent=2)
                
                elif uri.startswith("task://get/"):
                    task_id = uri.split("/")[-1]
                    response = await self.http_client.get(f"/api/tasks/{task_id}")
                    
                    if response.status_code == 404:
                        return json.dumps({"error": f"Task {task_id} not found"}, indent=2)
                    
                    response.raise_for_status()
                    return json.dumps(response.json(), indent=2)
                
                elif uri == "task://metrics":
                    response = await self.http_client.get("/api/analytics/metrics")
                    response.raise_for_status()
                    return json.dumps(response.json(), indent=2)
                
                elif uri == "task://pending":
                    response = await self.http_client.get("/api/tasks", params={"status": "pending"})
                    response.raise_for_status()
                    return json.dumps(response.json(), indent=2)
                
                elif uri == "task://completed":
                    response = await self.http_client.get("/api/tasks", params={"status": "completed"})
                    response.raise_for_status()
                    return json.dumps(response.json(), indent=2)
                
                else:
                    return json.dumps({"error": f"Unknown resource: {uri}"}, indent=2)
                    
            except httpx.HTTPError as e:
                logger.error(f"HTTP error reading resource {uri}: {e}")
                return json.dumps({"error": f"Failed to fetch resource: {str(e)}"}, indent=2)
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return json.dumps({"error": f"Internal error: {str(e)}"}, indent=2)
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            """List available prompts"""
            return [
                types.Prompt(
                    name="project_planning",
                    description="Interactive project planning with task breakdown",
                    arguments=[
                        types.PromptArgument(
                            name="project_description",
                            description="Description of the project to plan",
                            required=True
                        )
                    ]
                ),
                types.Prompt(
                    name="task_prioritization",
                    description="Help prioritize tasks based on impact and urgency",
                    arguments=[]
                ),
                types.Prompt(
                    name="daily_standup",
                    description="Generate a daily standup report from task data",
                    arguments=[
                        types.PromptArgument(
                            name="assignee_id",
                            description="ID of the team member (optional)",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="sprint_planning",
                    description="Plan a sprint with task selection and estimation",
                    arguments=[
                        types.PromptArgument(
                            name="sprint_duration",
                            description="Duration of the sprint in days",
                            required=True
                        ),
                        types.PromptArgument(
                            name="team_capacity",
                            description="Team capacity in story points",
                            required=True
                        )
                    ]
                ),
            ]
        
        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict) -> types.GetPromptResult:
            """Get a specific prompt"""
            
            if name == "project_planning":
                project_desc = arguments.get("project_description", "")
                return types.GetPromptResult(
                    description=f"Project planning assistant for: {project_desc}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"""I need help planning a project: {project_desc}

Please help me:
1. Break down the project into major milestones
2. Create specific tasks for each milestone
3. Suggest priorities and timelines
4. Identify potential dependencies between tasks

You can use the following tools:
- search_tasks: to see existing tasks
- create_task: to create new tasks
- update_task: to modify existing tasks

And these resources:
- task://list: to view all current tasks
- task://metrics: to see task analytics
- task://pending: to see pending tasks"""
                            )
                        )
                    ]
                )
            
            elif name == "task_prioritization":
                return types.GetPromptResult(
                    description="Task prioritization assistant",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text="""Please help me prioritize my tasks.

Use the task://list resource to see all current tasks, then suggest:
1. Which tasks should be done first (urgent and important)
2. Which tasks can be delegated or deferred
3. Any tasks that might be blocking others
4. A recommended order of execution

Consider factors like:
- Task dependencies
- Business impact
- Resource availability
- Deadlines

You can use the update_task tool to change task priorities and the bulk_update_tasks tool to update multiple tasks at once."""
                            )
                        )
                    ]
                )
            
            elif name == "daily_standup":
                assignee_id = arguments.get("assignee_id")
                filter_text = f" for assignee {assignee_id}" if assignee_id else ""
                
                return types.GetPromptResult(
                    description=f"Daily standup report generator{filter_text}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"""Generate a daily standup report{filter_text}.

Please analyze the tasks and provide:
1. What was completed yesterday (completed tasks)
2. What is planned for today (in_progress and high-priority pending tasks)
3. Any blockers or concerns (critical priority items, overdue tasks)

Use these resources:
- task://completed: to see completed tasks
- task://pending: to see pending tasks
- task://metrics: to get overall metrics

Format the report in a clear, concise manner suitable for a team standup meeting."""
                            )
                        )
                    ]
                )
            
            elif name == "sprint_planning":
                sprint_duration = arguments.get("sprint_duration", "14")
                team_capacity = arguments.get("team_capacity", "100")
                
                return types.GetPromptResult(
                    description=f"Sprint planning for {sprint_duration} days with {team_capacity} story points capacity",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"""Help me plan a sprint:
- Duration: {sprint_duration} days
- Team capacity: {team_capacity} story points

Please:
1. Review pending tasks using task://pending
2. Analyze task priorities and dependencies
3. Recommend which tasks to include in the sprint
4. Ensure the selected tasks fit within the team capacity
5. Identify any risks or dependencies

Use the search_tasks tool to filter tasks by priority and status.
Use the update_task or bulk_update_tasks tools to mark selected tasks for the sprint.

Provide a sprint plan with:
- Sprint goals
- Selected tasks with priorities
- Risk assessment
- Success criteria"""
                            )
                        )
                    ]
                )
            
            return types.GetPromptResult(
                description="Unknown prompt",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text="Unknown prompt requested"
                        )
                    )
                ]
            )
    
    async def run(self):
        """Run the MCP server using stdio transport"""
        logger.info("Starting MCP server with stdio transport...")
        
        # Use the stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("MCP server running on stdio")
            
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="task-management-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
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