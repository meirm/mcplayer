#!/usr/bin/env python3
"""
Backend API Application
Core business logic and data management layer
This is the actual backend that the MCP server will interact with
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn

# ============================================================================
# Database Configuration
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")  # Use SQLite for simplicity
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# Database Models
# ============================================================================

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskModel(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    assignee_id = Column(Integer, nullable=True)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# Pydantic Schemas
# ============================================================================

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    assignee_id: Optional[int] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None

class Task(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskList(BaseModel):
    tasks: List[Task]
    total: int
    limit: int
    offset: int
    has_more: bool

class BulkUpdateRequest(BaseModel):
    task_ids: List[int]
    update: TaskUpdate

class BulkUpdateResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    results: List[Dict[str, Any]]

class TaskMetrics(BaseModel):
    timeframe: str
    total_tasks: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    completion_rate: float
    average_tasks_per_user: float

# ============================================================================
# Database Dependency
# ============================================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# Service Layer
# ============================================================================

class TaskService:
    """Business logic for task management"""
    
    @staticmethod
    def create_task(db: Session, task_data: TaskCreate) -> TaskModel:
        db_task = TaskModel(**task_data.model_dump())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[TaskModel]:
        return db.query(TaskModel).filter(TaskModel.id == task_id).first()
    
    @staticmethod
    def get_tasks(
        db: Session,
        status: Optional[TaskStatus] = None,
        assignee_id: Optional[int] = None,
        priority: Optional[TaskPriority] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[TaskModel]:
        query = db.query(TaskModel)
        
        if status:
            query = query.filter(TaskModel.status == status)
        if assignee_id is not None:
            query = query.filter(TaskModel.assignee_id == assignee_id)
        if priority:
            query = query.filter(TaskModel.priority == priority)
        
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    def count_tasks(
        db: Session,
        status: Optional[TaskStatus] = None,
        assignee_id: Optional[int] = None,
        priority: Optional[TaskPriority] = None
    ) -> int:
        query = db.query(TaskModel)
        
        if status:
            query = query.filter(TaskModel.status == status)
        if assignee_id is not None:
            query = query.filter(TaskModel.assignee_id == assignee_id)
        if priority:
            query = query.filter(TaskModel.priority == priority)
        
        return query.count()
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[TaskModel]:
        db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not db_task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
    
    @staticmethod
    def calculate_metrics(db: Session, timeframe: str = "week") -> TaskMetrics:
        all_tasks = db.query(TaskModel).all()
        
        by_status = {}
        for status in TaskStatus:
            count = db.query(TaskModel).filter(TaskModel.status == status).count()
            by_status[status.value] = count
        
        by_priority = {}
        for priority in TaskPriority:
            count = db.query(TaskModel).filter(TaskModel.priority == priority).count()
            by_priority[priority.value] = count
        
        total = len(all_tasks)
        completed = by_status.get(TaskStatus.COMPLETED.value, 0)
        completion_rate = (completed / total * 100) if total > 0 else 0.0
        
        # Calculate average tasks per user
        assignees = db.query(TaskModel.assignee_id).distinct().filter(
            TaskModel.assignee_id.isnot(None)
        ).count()
        avg_per_user = (total / assignees) if assignees > 0 else 0.0
        
        return TaskMetrics(
            timeframe=timeframe,
            total_tasks=total,
            by_status=by_status,
            by_priority=by_priority,
            completion_rate=completion_rate,
            average_tasks_per_user=avg_per_user
        )

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Add seed data
    db = SessionLocal()
    try:
        # Check if we need to seed data
        if db.query(TaskModel).count() == 0:
            seed_tasks = [
                TaskCreate(title="Set up MCP architecture", description="Implement the 4-component MCP system", priority=TaskPriority.HIGH),
                TaskCreate(title="Create backend API", description="Build FastAPI backend with business logic", priority=TaskPriority.CRITICAL),
                TaskCreate(title="Implement MCP server", description="Create MCP server following best practices", priority=TaskPriority.HIGH),
                TaskCreate(title="Build HTTP bridge", description="Connect MCP to HTTP for web clients", priority=TaskPriority.HIGH),
                TaskCreate(title="Design frontend", description="Create React UI for task management", priority=TaskPriority.MEDIUM),
            ]
            
            for task_data in seed_tasks:
                TaskService.create_task(db, task_data)
    finally:
        db.close()
    
    yield
    # Shutdown

app = FastAPI(
    title="Task Management Backend API",
    description="Core business logic and data management",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Task Management Backend API",
        "version": "1.0.0"
    }

# Task CRUD Operations

@app.post("/api/tasks", response_model=Task)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    db_task = TaskService.create_task(db, task)
    return Task.model_validate(db_task)

@app.get("/api/tasks", response_model=TaskList)
async def list_tasks(
    status: Optional[TaskStatus] = None,
    assignee_id: Optional[int] = None,
    priority: Optional[TaskPriority] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get paginated list of tasks with optional filtering"""
    tasks = TaskService.get_tasks(db, status, assignee_id, priority, limit, offset)
    total = TaskService.count_tasks(db, status, assignee_id, priority)
    
    return TaskList(
        tasks=[Task.model_validate(t) for t in tasks],
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total
    )

@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task.model_validate(task)

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing task"""
    task = TaskService.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task.model_validate(task)

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    success = TaskService.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "message": f"Task {task_id} deleted"}

# Bulk Operations

@app.post("/api/tasks/bulk-update", response_model=BulkUpdateResponse)
async def bulk_update_tasks(
    request: BulkUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update multiple tasks at once"""
    results = []
    succeeded = 0
    failed = 0
    
    for task_id in request.task_ids:
        try:
            task = TaskService.update_task(db, task_id, request.update)
            if task:
                results.append({"id": task_id, "status": "success"})
                succeeded += 1
            else:
                results.append({"id": task_id, "status": "error", "error": "Task not found"})
                failed += 1
        except Exception as e:
            results.append({"id": task_id, "status": "error", "error": str(e)})
            failed += 1
    
    return BulkUpdateResponse(
        total=len(request.task_ids),
        succeeded=succeeded,
        failed=failed,
        results=results
    )

# Analytics

@app.get("/api/analytics/metrics", response_model=TaskMetrics)
async def get_task_metrics(
    timeframe: str = Query("week", regex="^(day|week|month|year)$"),
    db: Session = Depends(get_db)
):
    """Get task analytics and metrics"""
    return TaskService.calculate_metrics(db, timeframe)

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )