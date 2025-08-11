# MCP Server - Task Management Protocol Bridge

A Model Context Protocol (MCP) server that provides AI-friendly access to the task management system. This server exposes tools, resources, and prompts that can be used by AI assistants like Claude, ChatGPT, or other MCP-compatible clients.

## Features

- **MCP Protocol Implementation**: Fully compliant with MCP specification
- **Task Management Tools**: 5 comprehensive tools for task operations
- **Data Resources**: 5 resources for accessing task data and analytics
- **AI Prompts**: 4 specialized prompts for project management workflows
- **Stdio Transport**: Standard input/output communication for maximum compatibility
- **Backend Integration**: Connects to FastAPI backend via HTTP

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │───▶│   MCP Server    │───▶│   Backend API   │
│  (Claude, etc)  │    │   (stdio)       │    │   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
    MCP Protocol            HTTP Client             REST API
```

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure backend URL:**
```bash
export BACKEND_API_URL=http://localhost:8001
```

3. **Run the server:**
```bash
python mcp_server_stdio.py
```

## MCP Capabilities

### Tools (5 Available)

| Tool | Description | Parameters |
|------|-------------|------------|
| `create_task` | Create a new task | `title`, `description`, `priority`, `assignee_id`, `due_date` |
| `update_task` | Update existing task | `task_id`, `title`, `description`, `status`, `priority`, `assignee_id`, `due_date` |
| `delete_task` | Delete a task | `task_id` |
| `search_tasks` | Search and filter tasks | `status`, `priority`, `assignee_id`, `limit`, `offset` |
| `bulk_update_tasks` | Update multiple tasks | `task_ids`, `status`, `priority`, `assignee_id` |

### Resources (5 Available)

| Resource URI | Description | Content Type |
|--------------|-------------|--------------|
| `task://list` | All tasks with pagination | `application/json` |
| `task://get/{id}` | Specific task by ID | `application/json` |
| `task://metrics` | Task analytics and metrics | `application/json` |
| `task://pending` | All pending tasks | `application/json` |
| `task://completed` | All completed tasks | `application/json` |

### Prompts (4 Available)

| Prompt | Description | Arguments |
|--------|-------------|-----------|
| `project_planning` | Break down projects into tasks | `project_description` |
| `task_prioritization` | Analyze and prioritize existing tasks | None |
| `daily_standup` | Generate daily standup reports | `assignee_id` (optional) |
| `sprint_planning` | Plan sprints with task selection | `sprint_duration`, `team_capacity` |

## Usage Examples

### Tool Execution

```python
# Create a task
result = await session.call_tool("create_task", {
    "title": "Implement user authentication",
    "description": "Add OAuth2 support to the API",
    "priority": "high",
    "assignee_id": 1
})

# Update task status
result = await session.call_tool("update_task", {
    "task_id": 1,
    "status": "completed"
})

# Search for high-priority pending tasks
result = await session.call_tool("search_tasks", {
    "status": "pending",
    "priority": "high",
    "limit": 10
})

# Bulk update multiple tasks
result = await session.call_tool("bulk_update_tasks", {
    "task_ids": [1, 2, 3],
    "status": "completed"
})

# Delete a task
result = await session.call_tool("delete_task", {
    "task_id": 1
})
```

### Resource Reading

```python
# Get all tasks
tasks = await session.read_resource("task://list")

# Get specific task
task = await session.read_resource("task://get/1")

# Get task metrics
metrics = await session.read_resource("task://metrics")

# Get pending tasks only
pending = await session.read_resource("task://pending")

# Get completed tasks only  
completed = await session.read_resource("task://completed")
```

### Prompt Usage

```python
# Project planning prompt
prompt = await session.get_prompt("project_planning", {
    "project_description": "Build a real-time chat application"
})

# Task prioritization prompt
prompt = await session.get_prompt("task_prioritization", {})

# Daily standup prompt
prompt = await session.get_prompt("daily_standup", {
    "assignee_id": 1  # Optional
})

# Sprint planning prompt
prompt = await session.get_prompt("sprint_planning", {
    "sprint_duration": "14",
    "team_capacity": "100"
})
```

## Configuration

### Environment Variables

- `BACKEND_API_URL`: Backend API endpoint (default: `http://localhost:8001`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### Example Configuration

```bash
export BACKEND_API_URL=http://localhost:8001
export LOG_LEVEL=DEBUG
python mcp_server_stdio.py
```

## Integration Methods

### 1. Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "task-management": {
      "command": "python",
      "args": ["/path/to/mcp_server_stdio.py"],
      "env": {
        "BACKEND_API_URL": "http://localhost:8001"
      }
    }
  }
}
```

### 2. Direct MCP Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_task_server():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_stdio.py"],
        env={"BACKEND_API_URL": "http://localhost:8001"}
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Use the session to call tools, read resources, get prompts
            result = await session.call_tool("search_tasks", {"status": "pending"})
```

### 3. MCPO Integration (Recommended)

The MCP server can be exposed via MCPO (MCP-to-OpenAPI proxy):

```bash
mcpo --port 8003 --api-key "task-management-secret" -- python mcp_server_stdio.py
```

This creates REST API endpoints accessible at `http://localhost:8003`

## Tool Schemas

### Create Task Schema
```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string", "minLength": 1, "maxLength": 200},
    "description": {"type": "string", "maxLength": 1000},
    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
    "assignee_id": {"type": "integer"},
    "due_date": {"type": "string", "format": "date-time"}
  },
  "required": ["title"]
}
```

### Update Task Schema
```json
{
  "type": "object", 
  "properties": {
    "task_id": {"type": "integer"},
    "title": {"type": "string", "minLength": 1, "maxLength": 200},
    "description": {"type": "string", "maxLength": 1000},
    "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "cancelled"]},
    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
    "assignee_id": {"type": "integer"},
    "due_date": {"type": "string", "format": "date-time"}
  },
  "required": ["task_id"]
}
```

### Search Tasks Schema
```json
{
  "type": "object",
  "properties": {
    "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "cancelled"]},
    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
    "assignee_id": {"type": "integer"},
    "limit": {"type": "integer", "default": 50, "minimum": 1, "maximum": 100},
    "offset": {"type": "integer", "default": 0, "minimum": 0}
  }
}
```

## Response Formats

### Tool Success Response
```json
{
  "success": true,
  "task": {
    "id": 1,
    "title": "Task Title",
    "status": "pending",
    "priority": "high",
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00"
  },
  "message": "Task created successfully with ID: 1"
}
```

### Tool Error Response
```json
{
  "success": false,
  "error": "Task not found"
}
```

### Resource Response
```json
{
  "tasks": [...],
  "total": 10,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

## Logging

The server provides detailed logging for debugging:

```bash
INFO:mcp-server:Starting MCP server with stdio transport...
INFO:mcp-server:MCP server running on stdio
INFO:mcp-server:Reading resource: task://list
INFO:mcp-server:Calling tool: create_task with arguments: {'title': 'New Task'}
```

## Error Handling

The server handles various error conditions gracefully:

- **Backend API Unreachable**: Returns error with connection details
- **Invalid Tool Arguments**: Returns validation error with details
- **Resource Not Found**: Returns 404 error with resource information
- **Server Errors**: Returns 500 error with error details

## Testing

### Manual Testing

```bash
# Test MCP server directly
BACKEND_API_URL=http://localhost:8001 python test_mcp.py
```

### Unit Testing

```bash
pytest tests/test_mcp_server.py
```

## Development

### Adding New Tools

1. Define the tool in `handle_list_tools()`:
```python
types.Tool(
    name="new_tool",
    description="Description of the new tool",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param"]
    }
)
```

2. Implement the tool in `handle_call_tool()`:
```python
elif name == "new_tool":
    param = arguments.get("param")
    # Tool implementation
    result = await self.http_client.post("/api/endpoint", json={"param": param})
    return [types.TextContent(type="text", text=json.dumps(result.json()))]
```

### Adding New Resources

1. Define the resource in `handle_list_resources()`:
```python
types.Resource(
    uri="task://new_resource",
    name="New Resource",
    description="Description of the new resource",
    mimeType="application/json"
)
```

2. Implement the resource in `handle_read_resource()`:
```python
elif uri == "task://new_resource":
    response = await self.http_client.get("/api/new_endpoint")
    return json.dumps(response.json(), indent=2)
```

## Compatibility

- **MCP Version**: 1.0
- **Python Version**: 3.8+
- **Transport**: stdio (standard input/output)
- **AI Clients**: Claude Desktop, OpenWebUI (via MCPO), custom MCP clients

## Troubleshooting

### Common Issues

1. **Server Not Starting**:
   - Check Python dependencies: `pip install -r requirements.txt`
   - Verify Python version: `python --version`
   - Check for port conflicts if using TCP transport

2. **Backend Connection Issues**:
   - Verify backend is running: `curl http://localhost:8001/`
   - Check `BACKEND_API_URL` environment variable
   - Review server logs for connection errors

3. **Tool Execution Failures**:
   - Validate tool arguments match schema
   - Check backend API responses
   - Review MCP server logs for detailed errors

4. **Resource Reading Issues**:
   - Ensure resource URIs are correctly formatted
   - Check backend API endpoint availability
   - Verify resource permissions

### Debug Mode

Enable detailed debugging:

```bash
LOG_LEVEL=DEBUG BACKEND_API_URL=http://localhost:8001 python mcp_server_stdio.py
```

## Performance

- **HTTP Client Pooling**: Uses persistent HTTP connections to backend
- **Async Operations**: Fully asynchronous for high concurrency
- **Error Caching**: Caches backend connection errors to avoid spam
- **Resource Cleanup**: Proper cleanup of HTTP connections on shutdown

## Security

- **Input Validation**: All tool arguments validated against JSON schemas
- **HTTP Client Security**: Uses httpx with proper timeout and error handling
- **No Authentication**: MCP server relies on backend API security
- **Stdio Transport**: Secure communication via standard I/O

## License

MIT