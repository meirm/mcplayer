# Complete MCP Integration Demo

This document demonstrates the complete MCP (Model Context Protocol) integration with OpenAPI using MCPO wrapper, showcasing how to expose MCP servers through standard REST APIs for integration with tools like OpenWebUI.

## 🏗️ System Architecture

Our implementation consists of 5 main components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenWebUI     │───▶│   MCPO Proxy    │───▶│   MCP Server    │───▶│   Backend API   │
│  (HTTP Client)  │    │ (HTTP→MCP Conv) │    │ (MCP Protocol)  │    │  (Business)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │                       │
        │                       │                       │                       │
    Port 3000                Port 8003                stdio                 Port 8001
    (Web UI)                (OpenAPI)               (MCP Protocol)        (Task Management)
```

### Components:

1. **Backend API** (`apps/backend/`) - FastAPI-based task management system
2. **MCP Server** (`apps/mcp-server/`) - Protocol bridge to backend with tools, resources, and prompts
3. **MCPO Wrapper** (`apps/mcpo-wrapper/`) - Converts MCP protocol to OpenAPI REST endpoints
4. **MCP Client CLI** (`apps/mcp-client/`) - Command-line interface for direct MCP interaction
5. **MCP Bridge** (`apps/mcp-proxy/`) - Alternative HTTP bridge (standalone implementation)

## 🚀 Quick Start Demo

### 1. Start the Complete System

```bash
# Terminal 1: Start Backend API
cd apps/backend
python main.py
# ✅ Running on http://localhost:8001

# Terminal 2: Start MCPO Wrapper (exposes MCP as OpenAPI)
cd apps/mcpo-wrapper
BACKEND_API_URL=http://localhost:8001 mcpo --port 8003 --api-key "task-management-secret" -- python ../mcp-server/mcp_server_stdio.py
# ✅ Running on http://localhost:8003
# 📖 Docs: http://localhost:8003/docs
```

### 2. Test OpenAPI Integration

**View API Documentation:**
```bash
open http://localhost:8003/docs
```

**Create a Task via REST API:**
```bash
curl -X POST http://localhost:8003/create_task \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Integration Test Task",
    "description": "Created via MCPO OpenAPI wrapper",
    "priority": "high"
  }'
```

**Response:**
```json
{
  "success": true,
  "task": {
    "title": "Integration Test Task",
    "description": "Created via MCPO OpenAPI wrapper",
    "assignee_id": null,
    "priority": "high",
    "due_date": null,
    "id": 7,
    "status": "pending",
    "created_at": "2025-08-11T00:15:30.123456",
    "updated_at": "2025-08-11T00:15:30.123456"
  },
  "message": "Task created successfully with ID: 7"
}
```

**Search Tasks:**
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

### 3. Test MCP Client CLI

**Interactive CLI:**
```bash
cd apps/mcp-client
python mcp_client_cli.py
```

**CLI Commands:**
```
mcp> help                    # Show all commands
mcp> tools                   # List available MCP tools
mcp> resources               # List available MCP resources
mcp> create                  # Create task interactively
mcp> search pending high     # Search pending high-priority tasks
mcp> view 7                  # View specific task
mcp> metrics                 # Show analytics
mcp> prompt daily_standup    # Get AI standup prompt
```

## 📊 Available APIs

### Tools (via MCPO - POST endpoints)

| Endpoint | Description | Example |
|----------|-------------|---------|
| `/create_task` | Create new task | `{"title": "New Task", "priority": "high"}` |
| `/update_task` | Update existing task | `{"task_id": 1, "status": "completed"}` |
| `/delete_task` | Delete task | `{"task_id": 1}` |
| `/search_tasks` | Search/filter tasks | `{"status": "pending", "priority": "high"}` |
| `/bulk_update_tasks` | Update multiple tasks | `{"task_ids": [1,2,3], "status": "completed"}` |

### Resources (via MCP Client)

| Resource | Description | Access Method |
|----------|-------------|---------------|
| `task://list` | All tasks | MCP Client / CLI |
| `task://get/{id}` | Specific task | MCP Client / CLI |
| `task://metrics` | Analytics data | MCP Client / CLI |
| `task://pending` | Pending tasks | MCP Client / CLI |
| `task://completed` | Completed tasks | MCP Client / CLI |

### Prompts (via MCP Client)

| Prompt | Description | Parameters |
|--------|-------------|------------|
| `project_planning` | Project breakdown | `project_description` |
| `task_prioritization` | Task prioritization | None |
| `daily_standup` | Standup report | `assignee_id` (optional) |
| `sprint_planning` | Sprint planning | `sprint_duration`, `team_capacity` |

## 🔗 OpenWebUI Integration

### 1. Configure OpenWebUI

1. Start OpenWebUI
2. Go to **Admin Panel → Settings → Tools**
3. Add OpenAPI Tool Server:
   - **Name**: Task Management
   - **URL**: `http://localhost:8003`
   - **API Key**: `task-management-secret`

### 2. Available Functions in Chat

Once configured, you can use these functions in OpenWebUI chat:

- **"Create a high-priority task to fix the login bug"**
  - Uses `create_task` tool automatically
- **"Show me all pending tasks"** 
  - Uses `search_tasks` with status filter
- **"Mark tasks 1, 2, and 3 as completed"**
  - Uses `bulk_update_tasks` tool
- **"Delete task 5"**
  - Uses `delete_task` tool

### 3. Natural Language Interface

OpenWebUI will automatically:
- Parse user intent from natural language
- Map to appropriate MCP tools
- Execute API calls through MCPO
- Present results in conversational format

## 🧪 Test Scenarios

### Scenario 1: Complete Task Lifecycle

```bash
# 1. Create task
curl -X POST http://localhost:8003/create_task \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Lifecycle", "priority": "medium"}'
# Returns: task ID 8

# 2. Update task status
curl -X POST http://localhost:8003/update_task \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{"task_id": 8, "status": "in_progress"}'

# 3. Complete task
curl -X POST http://localhost:8003/update_task \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{"task_id": 8, "status": "completed"}'

# 4. Verify completion
curl -X POST http://localhost:8003/search_tasks \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

### Scenario 2: Bulk Operations

```bash
# Create multiple tasks, then bulk update
for i in {1..3}; do
  curl -X POST http://localhost:8003/create_task \
    -H "Authorization: Bearer task-management-secret" \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Bulk Task $i\", \"priority\": \"low\"}"
done

# Bulk update all to high priority
curl -X POST http://localhost:8003/bulk_update_tasks \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{"task_ids": [9, 10, 11], "priority": "high"}'
```

### Scenario 3: AI-Assisted Workflow

```bash
# Using MCP CLI for AI prompts
cd apps/mcp-client
python mcp_client_cli.py

# In CLI:
mcp> prompt project_planning
Project description: Build a real-time chat application
# Returns detailed project breakdown prompt

mcp> prompt task_prioritization  
# Returns task prioritization guidance

mcp> metrics
# Shows current task analytics
```

## 🔧 Configuration Options

### MCPO Configuration

**Single Server Mode:**
```bash
mcpo --port 8003 --api-key "secret" -- python mcp_server.py
```

**Multi-Server Config File:**
```json
{
  "mcpServers": {
    "tasks": {
      "command": "python",
      "args": ["mcp_server_stdio.py"],
      "env": {"BACKEND_API_URL": "http://localhost:8001"}
    },
    "calendar": {
      "command": "python", 
      "args": ["calendar_mcp_server.py"]
    }
  }
}
```

**Docker Deployment:**
```yaml
services:
  mcpo-proxy:
    build: ./apps/mcpo-wrapper
    ports:
      - "8003:8003"
    environment:
      - BACKEND_API_URL=http://backend:8001
    depends_on:
      - backend
```

## 📈 Benefits of This Architecture

### 1. **Protocol Flexibility**
- **MCP Protocol**: Rich, typed interface for AI tools
- **OpenAPI REST**: Standard HTTP API for web integration
- **Stdio Transport**: Lightweight, secure communication

### 2. **Integration Options**
- **Direct MCP**: Use MCP clients (Claude Desktop, etc.)
- **OpenAPI Tools**: Use with OpenWebUI, Postman, curl, etc.
- **Custom Clients**: Build your own using either protocol

### 3. **Security & Standards**
- **API Key Authentication**: Secure access control
- **Standard HTTP**: Familiar security model
- **Type Safety**: Schema validation on both protocols

### 4. **Scalability**
- **Microservice Architecture**: Independent scaling
- **Multi-Server Support**: One MCPO can proxy multiple MCP servers
- **Load Balancing**: Standard HTTP load balancing

### 5. **Developer Experience**
- **Auto Documentation**: Swagger UI generation
- **Rich CLI**: Interactive command-line interface
- **Hot Reload**: Config changes without restart
- **Error Handling**: Structured error responses

## 🎯 Use Cases

### 1. **OpenWebUI Integration**
- Natural language task management
- Conversational project planning
- AI-assisted prioritization

### 2. **API Development**
- RESTful task management API
- Third-party integrations
- Mobile app backends

### 3. **Automation**
- CI/CD pipeline integration
- Automated task creation
- Bulk operations via scripts

### 4. **Analytics & Reporting**
- Task metrics and KPIs
- Team productivity insights
- Project progress tracking

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using a port
   lsof -i :8003
   
   # Use different port
   mcpo --port 8004 --api-key "secret" -- python mcp_server.py
   ```

2. **Backend Connection**
   ```bash
   # Test backend directly
   curl http://localhost:8001/
   
   # Check environment variable
   echo $BACKEND_API_URL
   ```

3. **MCP Server Issues**
   ```bash
   # Test MCP server directly
   BACKEND_API_URL=http://localhost:8001 python mcp_server_stdio.py
   
   # Check dependencies
   pip install -r requirements.txt
   ```

### Logs and Monitoring

- **MCPO Logs**: Detailed request/response logging
- **Backend Logs**: API access and database operations  
- **MCP Logs**: Protocol-level communication
- **Health Checks**: Built-in health endpoints

## 📚 Next Steps

1. **Enhanced Security**: Add OAuth2, rate limiting
2. **Monitoring**: Add metrics, tracing, alerting
3. **Additional Tools**: Extend MCP server with more tools
4. **UI Components**: Build React components for task management
5. **Mobile Support**: Create mobile app using the OpenAPI

This integration demonstrates the power of MCP protocol with standard REST APIs, providing the best of both worlds for AI tool integration.