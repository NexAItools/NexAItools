"""
API routes for connecting the frontend to the backend.
This module contains the API endpoints for the Ashus AI system.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from src.persistence.database import get_db, TaskModel, MessageModel, AgentModel
from src.orchestration.task_manager import Task, TaskStatus
from src.orchestration.message_router import Message

router = APIRouter()

# Tasks endpoints
@router.get("/tasks", response_model=List[dict])
def get_tasks(db: Session = Depends(get_db), user_id: Optional[str] = None):
    """Get all tasks or tasks for a specific user."""
    query = db.query(TaskModel)
    if user_id:
        query = query.filter(TaskModel.user_id == user_id)
    tasks = query.all()
    return [task.to_dict() for task in tasks]

@router.get("/tasks/{task_id}", response_model=dict)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get a specific task by ID."""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return task.to_dict()

@router.post("/tasks", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_task(task_data: dict, db: Session = Depends(get_db)):
    """Create a new task."""
    task_id = str(uuid.uuid4())
    task_data["task_id"] = task_id
    task_model = TaskModel.from_dict(task_data)
    
    db.add(task_model)
    db.commit()
    db.refresh(task_model)
    
    return task_model.to_dict()

@router.put("/tasks/{task_id}", response_model=dict)
def update_task(task_id: str, task_data: dict, db: Session = Depends(get_db)):
    """Update a specific task."""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    # Update task fields
    for key, value in task_data.items():
        if key == "metadata" and value:
            setattr(task, key, json.dumps(value))
        elif key == "result" and value is not None:
            setattr(task, key, json.dumps(value))
        elif hasattr(task, key):
            setattr(task, key, value)
    
    task.updated_at = datetime.now()
    db.commit()
    db.refresh(task)
    
    return task.to_dict()

# Messages endpoints
@router.get("/messages", response_model=List[dict])
def get_messages(
    db: Session = Depends(get_db),
    sender_id: Optional[str] = None,
    recipient_id: Optional[str] = None
):
    """Get messages with optional filtering by sender or recipient."""
    query = db.query(MessageModel)
    if sender_id:
        query = query.filter(MessageModel.sender_id == sender_id)
    if recipient_id:
        query = query.filter(MessageModel.recipient_id == recipient_id)
    
    messages = query.all()
    return [message.to_dict() for message in messages]

@router.post("/messages", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_message(message_data: dict, db: Session = Depends(get_db)):
    """Create a new message and process it through the system."""
    message_id = str(uuid.uuid4())
    message_data["message_id"] = message_id
    
    # Create and save the message
    message_model = MessageModel.from_dict(message_data)
    db.add(message_model)
    db.commit()
    db.refresh(message_model)
    
    # Process the message through the message router
    # This would typically be done asynchronously
    from src.orchestration.message_router import MessageRouter
    router = MessageRouter()
    response = router.route_message(message_model.to_dict())
    
    # Save the response message
    if response:
        response_model = MessageModel.from_dict(response)
        db.add(response_model)
        db.commit()
        return response_model.to_dict()
    
    return message_model.to_dict()

# Agents endpoints
@router.get("/agents", response_model=List[dict])
def get_agents(db: Session = Depends(get_db), is_active: Optional[bool] = None):
    """Get all agents or only active/inactive agents."""
    query = db.query(AgentModel)
    if is_active is not None:
        query = query.filter(AgentModel.is_active == is_active)
    
    agents = query.all()
    return [agent.to_dict() for agent in agents]

@router.get("/agents/{agent_id}", response_model=dict)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get a specific agent by ID."""
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    return agent.to_dict()

# System status endpoint
@router.get("/status")
def get_system_status():
    """Get the current status of the Ashus AI system."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
