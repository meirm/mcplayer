# Backend API - Task Management System

FastAPI-based backend providing RESTful API for task management operations. This is the core business logic layer that handles data persistence, validation, and task operations.

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **SQLAlchemy ORM**: Database abstraction with SQLite for development
- **Task CRUD Operations**: Complete create, read, update, delete functionality
- **Bulk Operations**: Update multiple tasks simultaneously
- **Analytics API**: Task metrics and performance insights
- **Data Validation**: Pydantic models for request/response validation
- **Auto Documentation**: OpenAPI/Swagger documentation at `/docs`

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Server    │───▶│   Backend API   │───▶│    Database     │
│   (Port stdio)  │    │   (Port 8001)   │    │   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
    MCP Protocol            HTTP REST API           File Storage
```

## Installation

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the server:**
```bash
python main.py
```

The server will start on `http://localhost:8001`

## API Endpoints

### Task Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tasks` | List all tasks with filtering |
| `POST` | `/api/tasks` | Create a new task |
| `GET` | `/api/tasks/{id}` | Get specific task by ID |
| `PUT` | `/api/tasks/{id}` | Update existing task |
| `DELETE` | `/api/tasks/{id}` | Delete task |
| `POST` | `/api/tasks/bulk-update` | Update multiple tasks |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analytics/metrics` | Get task analytics and metrics |

### Query Parameters

**Task Listing (`GET /api/tasks`)**:
- `status`: Filter by status (`pending`, `in_progress`, `completed`, `cancelled`)
- `priority`: Filter by priority (`low`, `medium`, `high`, `critical`)
- `assignee_id`: Filter by assignee ID
- `limit`: Maximum results (default: 50, max: 100)
- `offset`: Pagination offset (default: 0)

**Analytics (`GET /api/analytics/metrics`)**:
- `timeframe`: Time period (`day`, `week`, `month`, `year`)

## Data Models

### Task Model

```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.pending
    assignee_id: Optional[int] = None
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None

class TaskResponse(TaskCreate):
    id: int
    created_at: datetime
    updated_at: datetime
```

### Enums

```python
class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
```

## Example Usage

### Create Task
```bash
curl -X POST "http://localhost:8001/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add OAuth2 authentication to the API",
    "priority": "high",
    "assignee_id": 1
  }'
```

### Update Task
```bash
curl -X PUT "http://localhost:8001/api/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "priority": "high"
  }'
```

### Search Tasks
```bash
curl "http://localhost:8001/api/tasks?status=pending&priority=high&limit=10"
```

### Bulk Update
```bash
curl -X POST "http://localhost:8001/api/tasks/bulk-update" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [1, 2, 3],
    "update": {
      "status": "completed"
    }
  }'
```

### Get Analytics
```bash
curl "http://localhost:8001/api/analytics/metrics?timeframe=week"
```

## Database Schema

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    status VARCHAR(20) NOT NULL,
    assignee_id INTEGER,
    priority VARCHAR(20) NOT NULL,
    due_date DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

## Configuration

### Environment Variables

- `DATABASE_URL`: Database connection string (default: `sqlite:///tasks.db`)
- `DEBUG`: Enable debug mode (default: `False`)
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8001`)

### Example .env file

```bash
DATABASE_URL=sqlite:///tasks.db
DEBUG=true
HOST=0.0.0.0
PORT=8001
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Linting
flake8 .

# Type checking
mypy .

# Formatting
black .
```

### Database Migrations

The application uses SQLAlchemy with automatic table creation. For production, consider using Alembic for migrations:

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Docker Support

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["python", "main.py"]
```

### Build and Run
```bash
docker build -t task-backend .
docker run -p 8001:8001 -e DATABASE_URL=sqlite:///data/tasks.db task-backend
```

## Health Check

The API includes a health check endpoint:

```bash
curl http://localhost:8001/
# Response: {"status": "healthy", "service": "Task Management Backend API", "version": "1.0.0"}
```

## Error Handling

The API returns structured error responses:

```json
{
  "detail": "Task not found"
}
```

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Logging

The backend logs all requests and errors. Configure logging level via environment:

```bash
LOG_LEVEL=INFO python main.py
```

## Performance

- **Database Connection Pooling**: SQLAlchemy manages connections
- **Async Support**: FastAPI with async/await for high concurrency
- **Pagination**: Built-in limit/offset pagination
- **Query Optimization**: Indexed database queries

## Security

- **Input Validation**: Pydantic models validate all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **CORS**: Configurable cross-origin resource sharing
- **Rate Limiting**: Consider adding rate limiting for production

## Integration

This backend is designed to work with:

- **MCP Server**: Provides MCP protocol interface
- **MCPO Proxy**: Exposes via OpenAPI for tools like OpenWebUI
- **Frontend**: React web interface
- **Third-party Apps**: Any HTTP client via REST API

## Production Deployment

### Gunicorn (Recommended)
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

### Environment Setup
- Use PostgreSQL or MySQL for production database
- Configure proper logging aggregation
- Set up monitoring and health checks
- Use reverse proxy (nginx) for SSL and load balancing

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check `DATABASE_URL` environment variable
   - Ensure SQLite file permissions for file-based databases
   - Verify database server is running for remote databases

2. **Port Already in Use**:
   - Change port: `PORT=8002 python main.py`
   - Find process using port: `lsof -i :8001`

3. **Import Errors**:
   - Activate virtual environment
   - Install dependencies: `pip install -r requirements.txt`

### Debug Mode

Enable detailed error messages:
```bash
DEBUG=true python main.py
```

This will provide stack traces and detailed error information.

## License

MIT