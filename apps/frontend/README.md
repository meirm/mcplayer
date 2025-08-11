# Task Management Frontend

A React TypeScript frontend for the task management system powered by MCPO (MCP-to-OpenAPI proxy).

## Features

- **Modern React UI**: Built with React 18 and TypeScript for type safety
- **MCPO Integration**: Connects to task management system via MCPO OpenAPI wrapper
- **REST API Interface**: Standard HTTP REST API calls instead of custom protocols
- **Responsive Design**: Works on desktop and mobile devices
- **Task Management**: Full CRUD operations for tasks
- **Bulk Operations**: Update multiple tasks at once
- **Rich Interactions**: Form validation, error handling, status management

## Architecture

The frontend now connects to MCPO (port 8003) which exposes MCP server capabilities as REST APIs:

```
Frontend (React) → MCPO Proxy (OpenAPI) → MCP Server (stdio) → Backend API (FastAPI)
     ↓                    ↓                      ↓                    ↓
  Port 3000           Port 8003               stdio              Port 8001
```

## Prerequisites

- Node.js 18+ and npm
- MCPO proxy running on port 8003
- Backend API running on port 8001

## Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment (optional):
```bash
cp .env.example .env.local
# Edit .env.local with your settings
```

## Development

Start the development server:

```bash
npm start
```

The application will be available at http://localhost:3000

## Environment Variables

- `REACT_APP_MCPO_URL`: MCPO proxy endpoint (default: http://localhost:8003)
- `REACT_APP_MCPO_API_KEY`: API key for MCPO authentication (default: task-management-secret)

## Building for Production

```bash
npm run build
```

The build will be output to the `build/` directory.

## Features Overview

### Task Operations

- **Create**: Add new tasks with title, description, priority, and assignee
- **Read**: View task lists via search API
- **Update**: Modify task status, priority, and other fields  
- **Delete**: Remove tasks with confirmation
- **Bulk Update**: Update multiple tasks at once

### API Integration

- Standard REST API calls with authentication
- OpenAPI schema discovery for available operations
- Error handling with user-friendly messages
- Form validation and data transformation

### UI/UX Features

- Responsive grid layout
- Color-coded priority and status indicators
- Checkbox selection for bulk operations
- Error banners and loading states
- Automatic refresh after operations

## Component Structure

```
src/
├── components/
│   ├── TaskManager.tsx    # Main task management component
│   └── TaskManager.css    # Component styles
├── hooks/
│   └── useMCP.ts         # MCPO integration hook
├── App.tsx               # Main application
└── index.tsx            # Entry point
```

## MCPO Integration

The frontend uses a custom React hook (`useMCP`) that provides:

- **Discovery**: Automatic detection of available tools from OpenAPI schema
- **Tool Execution**: REST API calls to MCPO endpoints with authentication
- **Error Handling**: Centralized error management and retry logic
- **Response Parsing**: Handles MCPO response format differences

### Key MCPO Operations

```typescript
const { executeTool, readResource, capabilities } = useMCP();

// Create a task
await executeTool('create_task', {
  title: 'New Task',
  description: 'Task description',
  priority: 'high'
});

// Read task list (via search_tasks)
const tasks = await readResource('tasks/list');

// Update task status
await executeTool('update_task', {
  task_id: 1,
  status: 'completed'
});

// Bulk update tasks
await executeTool('bulk_update_tasks', {
  task_ids: [1, 2, 3],
  status: 'completed'
});

// Delete task
await executeTool('delete_task', {
  task_id: 1
});
```

## Available MCPO Endpoints

The frontend uses these MCPO REST endpoints:

- `POST /create_task` - Create new task
- `POST /update_task` - Update existing task  
- `POST /delete_task` - Delete task
- `POST /search_tasks` - Search and filter tasks
- `POST /bulk_update_tasks` - Update multiple tasks
- `GET /openapi.json` - API schema discovery

## Docker Support

The frontend includes Docker configuration:

```bash
# Build image
docker build -t task-frontend .

# Run container  
docker run -p 3000:3000 \
  -e REACT_APP_MCPO_URL=http://mcpo:8003 \
  -e REACT_APP_MCPO_API_KEY=task-management-secret \
  task-frontend
```

## Testing

Run the test suite:

```bash
npm test
```

## Troubleshooting

### Connection Issues

1. **MCPO proxy not responding**:
   - Ensure MCPO is running on port 8003
   - Check `REACT_APP_MCPO_URL` environment variable
   - Test MCPO directly: `curl http://localhost:8003/openapi.json`

2. **Authentication issues**:
   - Verify `REACT_APP_MCPO_API_KEY` matches MCPO configuration
   - Check browser network tab for 401/403 errors
   - Test with curl: `curl -H "Authorization: Bearer task-management-secret" http://localhost:8003/create_task`

3. **Tasks not loading**:
   - Check browser developer console for errors
   - Verify backend API is running on port 8001
   - Check MCPO logs for MCP server connection issues

4. **Build issues**:
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

### API Response Format

MCPO returns responses in this format:

```json
{
  "success": true,
  "task": { ... },
  "message": "Task created successfully with ID: 1"
}
```

The frontend handles various response formats for compatibility.

## Integration with OpenWebUI

This frontend architecture is compatible with OpenWebUI integration:

1. MCPO provides standard OpenAPI endpoints
2. Same authentication and response format
3. Can be used alongside or instead of OpenWebUI
4. Shares the same backend infrastructure

## Contributing

1. Follow TypeScript best practices
2. Use functional components with hooks
3. Implement proper error boundaries
4. Add unit tests for new features
5. Follow the existing code style and patterns
6. Test with actual MCPO proxy server

## License

MIT