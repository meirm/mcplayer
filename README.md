# MCP Task Management System

A unified MCP (Model Context Protocol) architecture implementation that provides task management capabilities for both web frontends and AI agents through a single backend system. This project demonstrates how to build AI-native applications that treat AI agents and traditional UIs as equal citizens.

![MCP Task Management System – POC Frontend](poc_frontend.png)


**Author:** Meir Michanie (meirm@cyborg.fi)  
**Developed with:** Claude AI assistance for architecture design and implementation

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Browser   │     │    OpenWebUI    │     │    AI Agent     │
│   (React/TS)    │     │  (Chat Interface)│     │ (Claude/GPT)    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                         │
         │ HTTP/REST             │ HTTP/REST               │ MCP
         │                       │                         │
         ▼                       ▼                         │
┌─────────────────────────────────────────┐               │
│          MCPO (MCP-to-OpenAPI)          │               │
│           Proxy Layer                   │               │
│          (Port 8003)                    │               │
└────────────────┬────────────────────────┘               │
                 │                                         │
                 │ MCP (stdio)                            │
                 ▼                                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      MCP Server                               │
│                     (stdio transport)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Tools     │  │  Resources   │  │   Prompts    │      │
│  │  (5 tools)   │  │  (5 resources)│  │ (4 prompts)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               │ HTTP/REST
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                    Backend API                                │
│                   (FastAPI - Port 8001)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   SQLite    │  │   Task      │  │  Analytics  │          │
│  │  Database   │  │   CRUD      │  │   Metrics   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└───────────────────────────────────────────────────────────────┘
```

### Data Flow:
1. **Web Browser/OpenWebUI** → HTTP → **MCPO Proxy**  
2. **AI Agents** → Direct MCP → **MCP Server**
3. **MCPO Proxy** → MCP (stdio) → **MCP Server**
4. **MCP Server** → HTTP/REST → **Backend API**
5. **Backend API** → SQLite Database

## Components

### 1. Backend API (`apps/backend`)
- **Purpose**: Core business logic and data persistence
- **Technology**: FastAPI with SQLAlchemy ORM and SQLite database  
- **Features**: Complete task CRUD operations, analytics, bulk operations
- **Port**: 8001
- **Documentation**: [Backend README](apps/backend/README.md)

### 2. MCP Server (`apps/mcp-server`)  
- **Purpose**: MCP protocol interface to task management system
- **Technology**: Python MCP SDK with stdio transport
- **Capabilities**: 5 tools, 5 resources, 4 AI prompts
- **Transport**: stdio (standard input/output)
- **Documentation**: [MCP Server README](apps/mcp-server/README.md)

### 3. MCPO Proxy (`apps/mcpo-wrapper`)
- **Purpose**: MCP-to-OpenAPI translation layer  
- **Technology**: MCPO package (Python)
- **Features**: Auto-generated REST endpoints, OpenAPI documentation, API key auth
- **Port**: 8003
- **Documentation**: [MCPO Wrapper README](apps/mcpo-wrapper/README.md)

### 4. Frontend (`apps/frontend`)
- **Purpose**: Web-based task management interface
- **Technology**: React with TypeScript
- **Features**: Task CRUD, bulk operations, responsive design
- **Integration**: Connects to MCPO via REST API  
- **Port**: 3000 (development)
- **Documentation**: [Frontend README](apps/frontend/README.md)

## Prerequisites

- **Python 3.8+** (for backend, MCP server, MCPO)
- **Node.js 18+** and npm (for frontend)  
- **MCPO package**: `pip install mcpo`
- **Docker/Podman** (optional, for containerized deployment)

## Quick Start

### 🚀 Development Mode (Recommended)

Start each component in a separate terminal:

```bash
# Terminal 1: Backend API
cd apps/backend
pip install -r requirements.txt
python main.py
# Starts on http://localhost:8001

# Terminal 2: MCPO Proxy
cd apps/mcpo-wrapper  
pip install -r requirements.txt
BACKEND_API_URL=http://localhost:8001 mcpo \
  --port 8003 \
  --api-key "task-management-secret" \
  -- python ../mcp-server/mcp_server_stdio.py
# Starts on http://localhost:8003

# Terminal 3: Frontend (optional)
cd apps/frontend
npm install
REACT_APP_MCPO_URL=http://localhost:8003 \
REACT_APP_MCPO_API_KEY=task-management-secret \
npm start
# Starts on http://localhost:3000
```

### 🐳 Docker Mode

```bash
# Build and start all services
docker-compose build
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Access Points

- **🌐 Frontend UI**: http://localhost:3000 (React task management interface)
- **📋 MCPO API Docs**: http://localhost:8003/docs (Interactive OpenAPI documentation)
- **🔧 Backend API**: http://localhost:8001 (Direct backend access)
- **📊 Health Check**: http://localhost:8001/ (System health status)

## API Usage Examples

### Task Operations via MCPO

```bash
# Create a task
curl -X POST http://localhost:8003/create_task \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add OAuth2 support",
    "priority": "high",
    "assignee_id": 1
  }'

# Search tasks  
curl -X POST http://localhost:8003/search_tasks \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "pending",
    "priority": "high",
    "limit": 10
  }'

# Update task status
curl -X POST http://localhost:8003/update_task \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "status": "completed"
  }'

# Bulk update tasks
curl -X POST http://localhost:8003/bulk_update_tasks \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [1, 2, 3],
    "status": "completed"
  }'
```

## Key Features

### ✨ AI-Native Architecture
- **Unified Protocol**: Same MCP interface serves web UI, chat interfaces, and AI agents
- **Feature Parity**: Identical task operations available across all client types
- **OpenAPI Integration**: MCPO automatically generates REST API from MCP definitions

### 🔧 Task Management Capabilities  
- **Complete CRUD**: Create, read, update, delete tasks with validation
- **Bulk Operations**: Update multiple tasks simultaneously
- **Advanced Search**: Filter tasks by status, priority, assignee
- **Analytics**: Task metrics and completion statistics

### 🤖 AI Integration Features
- **MCP Tools (5)**: Direct task operations for AI agents
- **MCP Resources (5)**: Data access for task lists and metrics  
- **MCP Prompts (4)**: AI-assisted project planning and prioritization
- **OpenWebUI Ready**: Plug-and-play integration with chat interfaces

### 💻 Developer Experience
- **Type Safety**: End-to-end TypeScript from frontend to API
- **Auto Documentation**: Interactive OpenAPI docs at `/docs` endpoint
- **Hot Reload**: Development mode with instant updates
- **Container Ready**: Docker/Podman support for production deployment

## Integration Examples

### OpenWebUI Setup

1. **Configure Tool Integration**:
   - In OpenWebUI Admin → Settings → Tools
   - Add OpenAPI Tool: `http://localhost:8003`
   - API Key: `task-management-secret`

2. **Use in Chat**:
   ```
   "Create a high-priority task to fix the authentication bug"
   "Show me all pending tasks assigned to user 1"  
   "Mark tasks 1, 2, and 3 as completed"
   "Give me a project planning breakdown for a new mobile app"
   ```

### Claude Desktop Integration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "task-management": {
      "command": "python",
      "args": ["/path/to/apps/mcp-server/mcp_server_stdio.py"],
      "env": {
        "BACKEND_API_URL": "http://localhost:8001"
      }
    }
  }
}
```

### Custom MCP Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_task_mcp():
    server_params = StdioServerParameters(
        command="python",
        args=["apps/mcp-server/mcp_server_stdio.py"],
        env={"BACKEND_API_URL": "http://localhost:8001"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Create a task
            result = await session.call_tool("create_task", {
                "title": "API Integration Task",
                "priority": "medium"
            })
```

## Project Structure

```
mcplayer/
├── apps/
│   ├── backend/          # FastAPI backend (Port 8001)
│   ├── mcp-server/       # MCP stdio server 
│   ├── mcpo-wrapper/     # MCPO proxy (Port 8003)
│   └── frontend/         # React frontend (Port 3000)
├── RFC.md               # Architecture design document
├── CLAUDE.md           # Project context for Claude
├── API_EXAMPLES.md     # CRUD operation examples
└── README.md           # This file
```

## Testing & Verification

### Manual Testing

```bash
# Test backend API directly
curl http://localhost:8001/

# Test MCPO proxy
curl http://localhost:8003/openapi.json

# Test task creation
curl -X POST http://localhost:8003/create_task \
  -H "Authorization: Bearer task-management-secret" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "priority": "medium"}'

# Test MCP server directly (requires MCP client)
echo '{"title": "Direct MCP Test"}' | python apps/mcp-server/mcp_server_stdio.py
```

### Integration Testing  

1. **Frontend ↔ MCPO**: Create/update tasks via web UI
2. **MCPO ↔ MCP Server**: Check OpenAPI docs for all available tools
3. **MCP Server ↔ Backend**: Verify task persistence in backend  
4. **AI Integration**: Test with OpenWebUI or Claude Desktop

## Troubleshooting

### Common Issues

1. **Port conflicts**: 
   - Backend: `lsof -i :8001`
   - MCPO: `lsof -i :8003`
   - Frontend: `lsof -i :3000`

2. **MCPO connection issues**:
   - Check backend is running: `curl http://localhost:8001/`
   - Verify MCP server: Test standalone with `python apps/mcp-server/mcp_server_stdio.py`
   - Check MCPO logs for MCP server connection errors

3. **Authentication failures**:
   - Verify API key: `task-management-secret`
   - Check Authorization header format: `Bearer <key>`
   - Test with curl examples above

4. **Frontend not loading tasks**:
   - Check browser dev console for errors
   - Verify REACT_APP_MCPO_URL and REACT_APP_MCPO_API_KEY
   - Test MCPO endpoints manually with curl

## Architecture Benefits

This implementation demonstrates several key architectural benefits:

- ✅ **Single Source of Truth**: Business logic defined once, consumed by multiple clients
- ✅ **Protocol Flexibility**: MCP for AI agents, REST for web tools, same underlying capabilities  
- ✅ **Feature Parity**: AI and web interfaces have identical task management capabilities
- ✅ **Standard Integration**: Works with OpenWebUI, Claude Desktop, and any OpenAPI client
- ✅ **Developer Experience**: Strong typing, auto-generated docs, hot reload development

## Related Documentation

- **[RFC.md](RFC.md)**: Complete architecture design and implementation details
- **[API_EXAMPLES.md](API_EXAMPLES.md)**: Comprehensive CRUD operation examples
- **[Backend README](apps/backend/README.md)**: FastAPI backend implementation
- **[MCP Server README](apps/mcp-server/README.md)**: MCP protocol interface details  
- **[MCPO Wrapper README](apps/mcpo-wrapper/README.md)**: OpenAPI proxy configuration
- **[Frontend README](apps/frontend/README.md)**: React application setup

## Use Cases

### 🤖 AI-First Development
Perfect for teams building AI-native applications where AI agents are primary interfaces, with web UIs as secondary access methods.

### 🔄 API Unification  
Ideal for organizations wanting to eliminate duplicate API maintenance between human and AI interfaces.

### 🚀 Rapid Prototyping
Excellent for quickly building systems that need both conversational AI and traditional web interfaces.

### 📈 Future-Proof Architecture
Designed for the emerging paradigm where AI agents and humans collaborate seamlessly on the same tasks.

## Development Process

This project was developed through iterative collaboration between human expertise and AI assistance:

1. **Architecture Design**: Initial MCP architecture concepts and RFC document structure
2. **Implementation Planning**: Breaking down the system into manageable components
3. **Development**: Writing backend APIs, MCP servers, and frontend integration
4. **Integration**: Connecting components through MCPO and testing the complete system
5. **Documentation**: Creating comprehensive guides for each component and use case

The development process demonstrates effective human-AI collaboration in complex software architecture, from initial concept through working implementation.

## License

MIT - Feel free to use this architecture in your own projects.

## Support

- **Author**: Meir Michanie (meirm@cyborg.fi)
- **Issues**: Report bugs or request features via GitHub Issues  
- **Architecture Questions**: See RFC.md for detailed design decisions
- **Integration Help**: Each component has dedicated README with setup instructions