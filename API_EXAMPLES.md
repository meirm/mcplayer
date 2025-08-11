# Task Management API - CRUD Examples

This document provides examples of all CRUD operations available in the Task Management Backend API.

## Base URL
```
http://localhost:8001
```

## Health Check

### Check API Status
```bash
curl -X GET "http://localhost:8001/" | jq
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Task Management Backend API",
  "version": "1.0.0"
}
```

## Task Operations

### 1. List All Tasks
```bash
curl -X GET "http://localhost:8001/api/tasks" | jq
```

**Response:**
```json
{
  "tasks": [
    {
      "title": "Set up MCP architecture",
      "description": "Implement the 4-component MCP system",
      "assignee_id": null,
      "priority": "high",
      "due_date": null,
      "id": 1,
      "status": "pending",
      "created_at": "2025-08-10T23:45:24.850328",
      "updated_at": "2025-08-10T23:45:24.850331"
    },
    {
      "title": "Create backend API",
      "description": "Build FastAPI backend with business logic",
      "assignee_id": null,
      "priority": "critical",
      "due_date": null,
      "id": 2,
      "status": "pending",
      "created_at": "2025-08-10T23:45:24.851667",
      "updated_at": "2025-08-10T23:45:24.851669"
    }
  ],
  "total": 5,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

### 2. Create a New Task
```bash
curl -X POST "http://localhost:8001/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task via CURL",
    "description": "This is a test task created via curl",
    "priority": "medium",
    "assignee_id": 1
  }' | jq
```

**Response:**
```json
{
  "title": "Test Task via CURL",
  "description": "This is a test task created via curl",
  "assignee_id": 1,
  "priority": "medium",
  "due_date": null,
  "id": 6,
  "status": "pending",
  "created_at": "2025-08-10T23:47:53.321799",
  "updated_at": "2025-08-10T23:47:53.321801"
}
```

### 3. Get a Single Task
```bash
curl -X GET "http://localhost:8001/api/tasks/6" | jq
```

**Response:**
```json
{
  "title": "Test Task via CURL",
  "description": "This is a test task created via curl",
  "assignee_id": 1,
  "priority": "medium",
  "due_date": null,
  "id": 6,
  "status": "pending",
  "created_at": "2025-08-10T23:47:53.321799",
  "updated_at": "2025-08-10T23:47:53.321801"
}
```

### 4. Update a Task
```bash
curl -X PUT "http://localhost:8001/api/tasks/6" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "high"
  }' | jq
```

**Response:**
```json
{
  "title": "Test Task via CURL",
  "description": "This is a test task created via curl",
  "assignee_id": 1,
  "priority": "high",
  "due_date": null,
  "id": 6,
  "status": "in_progress",
  "created_at": "2025-08-10T23:47:53.321799",
  "updated_at": "2025-08-10T23:48:01.990634"
}
```

### 5. Bulk Update Tasks
```bash
curl -X POST "http://localhost:8001/api/tasks/bulk-update" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [1, 2, 3],
    "update": {
      "status": "completed"
    }
  }' | jq
```

**Response:**
```json
{
  "total": 3,
  "succeeded": 3,
  "failed": 0,
  "results": [
    {
      "id": 1,
      "status": "success"
    },
    {
      "id": 2,
      "status": "success"
    },
    {
      "id": 3,
      "status": "success"
    }
  ]
}
```

### 6. Filter Tasks by Status
```bash
curl -X GET "http://localhost:8001/api/tasks?status=completed" | jq
```

**Response:**
```json
{
  "tasks": [
    {
      "title": "Set up MCP architecture",
      "description": "Implement the 4-component MCP system",
      "assignee_id": null,
      "priority": "high",
      "due_date": null,
      "id": 1,
      "status": "completed",
      "created_at": "2025-08-10T23:45:24.850328",
      "updated_at": "2025-08-10T23:48:09.356162"
    },
    {
      "title": "Create backend API",
      "description": "Build FastAPI backend with business logic",
      "assignee_id": null,
      "priority": "critical",
      "due_date": null,
      "id": 2,
      "status": "completed",
      "created_at": "2025-08-10T23:45:24.851667",
      "updated_at": "2025-08-10T23:48:09.357329"
    }
  ],
  "total": 3,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

### 7. Delete a Task
```bash
curl -X DELETE "http://localhost:8001/api/tasks/6" | jq
```

**Response:**
```json
{
  "success": true,
  "message": "Task 6 deleted"
}
```

## Analytics

### Get Task Metrics
```bash
curl -X GET "http://localhost:8001/api/analytics/metrics" | jq
```

**Response:**
```json
{
  "timeframe": "week",
  "total_tasks": 5,
  "by_status": {
    "pending": 2,
    "in_progress": 0,
    "completed": 3,
    "cancelled": 0
  },
  "by_priority": {
    "low": 0,
    "medium": 1,
    "high": 3,
    "critical": 1
  },
  "completion_rate": 60.0,
  "average_tasks_per_user": 0.0
}
```

## Query Parameters

### Task List Filters
The `/api/tasks` endpoint supports the following query parameters:

- `status`: Filter by task status (`pending`, `in_progress`, `completed`, `cancelled`)
- `assignee_id`: Filter by assigned user ID
- `priority`: Filter by priority (`low`, `medium`, `high`, `critical`)
- `limit`: Maximum number of results (default: 50, max: 100)
- `offset`: Number of results to skip for pagination (default: 0)

**Example with multiple filters:**
```bash
curl -X GET "http://localhost:8001/api/tasks?status=pending&priority=high&limit=10" | jq
```

## Task Schema

### Task Fields
- `id`: Integer (auto-generated)
- `title`: String (required, 1-200 characters)
- `description`: String (optional, max 1000 characters)
- `status`: Enum (`pending`, `in_progress`, `completed`, `cancelled`)
- `assignee_id`: Integer (optional)
- `priority`: Enum (`low`, `medium`, `high`, `critical`)
- `due_date`: DateTime (optional, ISO format)
- `created_at`: DateTime (auto-generated)
- `updated_at`: DateTime (auto-updated)

### Priority Levels
- `low`: Low priority tasks
- `medium`: Medium priority tasks (default)
- `high`: High priority tasks
- `critical`: Critical priority tasks

### Status Values
- `pending`: Task not started (default)
- `in_progress`: Task currently being worked on
- `completed`: Task finished successfully
- `cancelled`: Task cancelled

## Error Responses

### 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Running the Backend

To start the backend API server:

```bash
cd apps/backend
python main.py
```

The server will start on `http://localhost:8001`

## API Documentation

When the server is running, you can access:
- Interactive API docs: http://localhost:8001/docs
- Alternative API docs: http://localhost:8001/redoc