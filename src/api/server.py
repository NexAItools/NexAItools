"""
API server for the Open Source Manus AI system.
"""

import logging
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import API_HOST, API_PORT, API_DEBUG, ALLOWED_ORIGINS
from src.orchestration.task_manager import TaskManager, Task, TaskStatus

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Open Source Manus AI API",
    description="API for interacting with the Open Source Manus AI system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize task manager
task_manager = TaskManager()

# Pydantic models for API
class TaskCreate(BaseModel):
    description: str = Field(..., description="Description of the task to be executed")
    user_id: Optional[str] = Field(None, description="ID of the user creating the task")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the task")

class TaskResponse(BaseModel):
    task_id: str = Field(..., description="Unique identifier for the task")
    description: str = Field(..., description="Description of the task")
    status: str = Field(..., description="Current status of the task")
    created_at: str = Field(..., description="Timestamp when the task was created")
    updated_at: str = Field(..., description="Timestamp when the task was last updated")
    user_id: Optional[str] = Field(None, description="ID of the user who created the task")
    result: Optional[Any] = Field(None, description="Result of the task execution, if completed")
    error: Optional[str] = Field(None, description="Error message, if task failed")

class TaskList(BaseModel):
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    count: int = Field(..., description="Total number of tasks")

# API endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Open Source Manus AI API",
        "version": "0.1.0",
        "status": "operational"
    }

@app.post("/tasks", response_model=TaskResponse, tags=["Tasks"])
async def create_task(task_data: TaskCreate, background_tasks: BackgroundTasks):
    """Create a new task."""
    logger.info(f"Creating new task: {task_data.description}")
    
    task = task_manager.create_task(
        description=task_data.description,
        user_id=task_data.user_id,
        metadata=task_data.metadata
    )
    
    # Execute task in background
    from src.agents.executor import ExecutorAgent
    executor = ExecutorAgent(task_manager)
    background_tasks.add_task(executor.execute_task, task)
    
    return TaskResponse(
        task_id=task.task_id,
        description=task.description,
        status=task.status.value,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
        user_id=task.user_id,
        result=task.result,
        error=task.error
    )

@app.get("/tasks", response_model=TaskList, tags=["Tasks"])
async def list_tasks(user_id: Optional[str] = None, status: Optional[str] = None):
    """List all tasks, optionally filtered by user ID or status."""
    tasks = []
    
    if user_id:
        tasks = task_manager.get_tasks_by_user(user_id)
    elif status:
        try:
            task_status = TaskStatus(status)
            tasks = task_manager.get_tasks_by_status(task_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    else:
        tasks = list(task_manager.tasks.values())
    
    task_responses = [
        TaskResponse(
            task_id=task.task_id,
            description=task.description,
            status=task.status.value,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            user_id=task.user_id,
            result=task.result,
            error=task.error
        )
        for task in tasks
    ]
    
    return TaskList(tasks=task_responses, count=len(task_responses))

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(task_id: str):
    """Get a specific task by ID."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return TaskResponse(
        task_id=task.task_id,
        description=task.description,
        status=task.status.value,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
        user_id=task.user_id,
        result=task.result,
        error=task.error
    )

@app.delete("/tasks/{task_id}", tags=["Tasks"])
async def delete_task(task_id: str):
    """Delete a specific task by ID."""
    success = task_manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return {"message": f"Task {task_id} deleted successfully"}

def start_api_server():
    """Start the API server."""
    import uvicorn
    logger.info(f"Starting API server on {API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)

if __name__ == "__main__":
    start_api_server()
