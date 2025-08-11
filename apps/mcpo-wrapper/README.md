# MCPO Wrapper - MCP to OpenAPI Proxy

MCPO (Model Context Protocol to OpenAPI) wrapper that exposes MCP server capabilities as standard REST API endpoints. This enables integration with tools like OpenWebUI, curl, Postman, and any HTTP client while maintaining the rich functionality of MCP protocol.

## Features

- **Protocol Translation**: Converts MCP protocol to REST API automatically
- **OpenAPI Documentation**: Auto-generated Swagger UI and OpenAPI spec
- **Authentication**: API key-based authentication for secure access
- **Multi-Server Support**: Can proxy multiple MCP servers simultaneously
- **Hot Reload**: Configuration changes without server restart
- **Docker Ready**: Complete containerization support

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTTP Client   │───▶│   MCPO Proxy    │───▶│   MCP Server    │───▶│   Backend API   │
│ (OpenWebUI/curl)│    │   (Port 8003)   │    │   (stdio)       │    │   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │                       │
    HTTP REST              OpenAPI Proxy          MCP Protocol             Business Logic
```

## Installation

### Method 1: Using pip (Recommended)

```bash
pip install mcpo
```

### Method 2: Using uv (Fastest)

```bash
uvx mcpo --port 8003 --api-key "task-management-secret" -- python ../mcp-server/mcp_server_stdio.py
```

### Method 3: Local Development

```bash
pip install -r requirements.txt
python setup_mcpo.py --install
```

## Quick Start

### Single MCP Server

```bash
# Start MCPO with our task management MCP server
BACKEND_API_URL=http://localhost:8001 mcpo \
  --port 8003 \
  --api-key "task-management-secret" \
  -- python ../mcp-server/mcp_server_stdio.py
```

**Available at:**
- API Base: `http://localhost:8003`
- Documentation: `http://localhost:8003/docs`
- OpenAPI Spec: `http://localhost:8003/openapi.json`

### Multiple MCP Servers

Create a configuration file (`config/mcpo_config.json`):

```json
{
  "mcpServers": {
    "task-management": {
      "command": "python",
      "args": ["../mcp-server/mcp_server_stdio.py"],
      "env": {
        "BACKEND_API_URL": "http://localhost:8001"
      },
      "description": "Task Management MCP Server"
    }
  }
}
```

Run with config:
```bash
mcpo --port 8003 --api-key "task-management-secret" --config config/mcpo_config.json
```

**Multi-server endpoints:**
- Main docs: `http://localhost:8003/docs`
- Task management: `http://localhost:8003/task-management/docs`

## Configuration

### Command Line Options

```bash
python setup_mcpo.py [options]

Options:
  --port PORT           MCPO server port (default: 8003)
  --backend-url URL     Backend API URL (default: http://localhost:8001)  
  --api-key KEY         API key for authentication (default: task-management-secret)
  --mode {single,config} Run mode (default: single)
  --install             Install MCPO if not present
  --test                Test API endpoints after startup
```

### Environment Variables

- `BACKEND_API_URL`: Backend API endpoint
- `MCPO_PORT`: Server port
- `MCPO_API_KEY`: Authentication key

## API Endpoints

MCPO automatically converts MCP tools to REST endpoints:

### Task Management Tools

| HTTP Method | Endpoint | MCP Tool | Description |
|-------------|----------|----------|-------------|
| `POST` | `/create_task` | `create_task` | Create new task |
| `POST` | `/update_task` | `update_task` | Update existing task |
| `POST` | `/delete_task` | `delete_task` | Delete task |
| `POST` | `/search_tasks` | `search_tasks` | Search and filter tasks |
| `POST` | `/bulk_update_tasks` | `bulk_update_tasks` | Update multiple tasks |

### Authentication

All endpoints require API key authentication:

```bash
curl -H "Authorization: Bearer task-management-secret" \
  http://localhost:8003/create_task
```

## Usage Examples

### Create Task

```bash
curl -X POST http://localhost:8003/create_task \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement OAuth2",
    "description": "Add authentication to the API",
    "priority": "high",
    "assignee_id": 1
  }'
```

**Response:**
```json
{
  "success": true,
  "task": {
    "id": 7,
    "title": "Implement OAuth2",
    "status": "pending",
    "priority": "high",
    "created_at": "2025-08-11T00:30:00"
  },
  "message": "Task created successfully with ID: 7"
}
```

### Search Tasks

```bash
curl -X POST http://localhost:8003/search_tasks \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "pending",
    "priority": "high",
    "limit": 10
  }'
```

### Update Task

```bash
curl -X POST http://localhost:8003/update_task \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 7,
    "status": "completed"
  }'
```

### Bulk Update

```bash
curl -X POST http://localhost:8003/bulk_update_tasks \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [1, 2, 3],
    "status": "completed"
  }'
```

### Delete Task

```bash
curl -X POST http://localhost:8003/delete_task \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 7
  }'
```

## OpenWebUI Integration

### Setup Steps

1. **Start MCPO**:
```bash
python setup_mcpo.py --mode config --port 8003
```

2. **Configure OpenWebUI**:
   - Go to **Admin Panel → Settings → Tools**
   - Add OpenAPI Tool Server:
     - **Name**: Task Management
     - **URL**: `http://localhost:8003`
     - **API Key**: `task-management-secret`

3. **Use in Chat**:
   - "Create a high-priority task to fix the login bug"
   - "Show me all pending tasks"
   - "Mark tasks 1, 2, and 3 as completed"

### Multi-Server Configuration

For multiple MCP servers, add each tool individually:

```json
{
  "tools": [
    {
      "name": "Task Management",
      "url": "http://localhost:8003/task-management",
      "apiKey": "task-management-secret"
    }
  ]
}
```

## Docker Deployment

### Simple Deployment

```bash
docker build -t mcpo-wrapper .
docker run -p 8003:8003 \
  -e BACKEND_API_URL=http://backend:8001 \
  -e MCPO_API_KEY=task-management-secret \
  mcpo-wrapper
```

### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ../backend
    ports: ["8001:8001"]
  
  mcpo-proxy:
    build: .
    ports: ["8003:8003"]
    environment:
      - BACKEND_API_URL=http://backend:8001
      - MCPO_API_KEY=task-management-secret
    depends_on: [backend]
```

Run with: `docker-compose up -d`

## Advanced Configuration

### Custom MCP Server Configuration

```json
{
  "mcpServers": {
    "tasks": {
      "command": "python",
      "args": ["mcp_server_stdio.py"],
      "env": {
        "BACKEND_API_URL": "http://localhost:8001",
        "LOG_LEVEL": "DEBUG"
      },
      "description": "Task management with full CRUD operations"
    },
    "calendar": {
      "command": "python",
      "args": ["calendar_server.py"],
      "env": {
        "CALENDAR_API": "http://localhost:9000"
      }
    }
  }
}
```

### Hot Reload Configuration

Enable automatic config reloading:

```bash
mcpo --port 8003 --config config.json --hot-reload
```

Changes to config.json will automatically restart affected servers.

### Health Checks

MCPO provides health check endpoints:

```bash
curl http://localhost:8003/health
# Response: {"status": "healthy", "servers": {"task-management": "connected"}}
```

## Monitoring and Logging

### Request Logging

MCPO logs all requests and responses:

```
2025-08-11 02:08:23 - INFO - Starting MCPO Server...
2025-08-11 02:08:24 - INFO - MCP server connected: task-management-mcp
2025-08-11 02:08:30 - INFO - POST /create_task - 200 - 45ms
```

### Performance Monitoring

Monitor MCPO performance:

```bash
curl http://localhost:8003/metrics
# Response includes request counts, response times, error rates
```

### Error Tracking

Errors are logged with full context:

```
2025-08-11 02:08:35 - ERROR - Tool execution failed: create_task
  Arguments: {"title": ""}
  Error: ValidationError: title field required
```

## Development

### Local Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with hot reload
python setup_mcpo.py --mode config --test --port 8003
```

### Testing the API

```bash
# Automated testing
python setup_mcpo.py --test

# Manual testing
curl -H "Authorization: Bearer task-management-secret" \
  http://localhost:8003/openapi.json
```

### Custom MCPO Wrapper

Create your own wrapper script:

```python
#!/usr/bin/env python3
from mcpo_wrapper.setup_mcpo import MCPOWrapper

async def main():
    wrapper = MCPOWrapper(
        mcpo_port=8003,
        backend_url="http://localhost:8001",
        api_key="my-secret-key"
    )
    
    await wrapper.start_mcpo_single()
    await wrapper.test_api()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Performance Optimization

### Caching

MCPO includes intelligent caching:

- **Schema Caching**: OpenAPI schemas cached for faster responses
- **Connection Pooling**: HTTP connections reused for efficiency
- **Response Caching**: Tool responses cached for repeated calls

### Concurrency

- **Async Processing**: Full async/await support for high concurrency
- **Connection Limits**: Configurable connection pool sizes
- **Rate Limiting**: Built-in rate limiting to prevent abuse

### Resource Usage

- **Memory Efficient**: Minimal memory footprint
- **CPU Optimized**: Efficient JSON processing and HTTP handling
- **Network Optimized**: Persistent connections and compression

## Troubleshooting

### Common Issues

1. **MCPO Won't Start**:
```bash
# Check if port is in use
lsof -i :8003

# Try different port
python setup_mcpo.py --port 8004
```

2. **MCP Server Connection Failed**:
```bash
# Test MCP server directly
BACKEND_API_URL=http://localhost:8001 python ../mcp-server/mcp_server_stdio.py

# Check backend API
curl http://localhost:8001/
```

3. **Authentication Issues**:
```bash
# Test with correct API key
curl -H "Authorization: Bearer task-management-secret" \
  http://localhost:8003/openapi.json

# Check for typos in API key
echo $MCPO_API_KEY
```

4. **OpenWebUI Integration Issues**:
   - Ensure MCPO URL is accessible from OpenWebUI
   - Verify API key matches exactly
   - Check OpenWebUI logs for connection errors
   - Test endpoints manually with curl first

### Debug Mode

Enable detailed debugging:

```bash
LOG_LEVEL=DEBUG python setup_mcpo.py --mode single --port 8003
```

This provides detailed logs of:
- MCP server communication
- HTTP request/response details
- Authentication attempts
- Error stack traces

### Performance Issues

Monitor and optimize performance:

```bash
# Check response times
curl -w "Time: %{time_total}s\n" \
  -H "Authorization: Bearer task-management-secret" \
  http://localhost:8003/search_tasks

# Monitor resource usage
top -p $(pgrep -f mcpo)

# Check connection stats
netstat -an | grep 8003
```

## Security Considerations

- **API Key Management**: Store API keys securely, rotate regularly
- **HTTPS in Production**: Use reverse proxy for SSL termination
- **Rate Limiting**: Configure appropriate rate limits for your use case
- **Network Security**: Restrict access to trusted networks only
- **Input Validation**: MCPO validates all inputs against MCP schemas

## Integration Examples

### Python Client

```python
import httpx

async def create_task_via_mcpo():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8003/create_task",
            headers={"Authorization": "Bearer task-management-secret"},
            json={
                "title": "Python API Integration",
                "priority": "medium"
            }
        )
        return response.json()
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

async function searchTasks() {
  const response = await axios.post(
    'http://localhost:8003/search_tasks',
    { status: 'pending', limit: 5 },
    {
      headers: {
        'Authorization': 'Bearer task-management-secret',
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
}
```

## Benefits

1. **Standard Interface**: Uses familiar REST API patterns
2. **Easy Integration**: Works with any HTTP client or OpenAPI tool
3. **Auto Documentation**: Generates interactive API documentation
4. **Security Layer**: Adds authentication to MCP servers
5. **Scalability**: Can proxy multiple MCP servers with load balancing
6. **Future-Proof**: REST APIs have long-term ecosystem support

## License

MIT