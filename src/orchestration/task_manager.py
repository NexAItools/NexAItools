"""
Orchestration layer for managing tasks, agents, and message routing.
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Enum representing the possible states of a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    """
    Represents a task to be executed by the system.
    """
    def __init__(
        self, 
        task_id: Optional[str] = None,
        description: str = "",
        user_id: Optional[str] = None,
        status: TaskStatus = TaskStatus.PENDING,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_task_id: Optional[str] = None
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.description = description
        self.user_id = user_id
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.metadata = metadata or {}
        self.parent_task_id = parent_task_id
        self.subtasks: List[Task] = []
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "user_id": self.user_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "parent_task_id": self.parent_task_id,
            "subtasks": [subtask.task_id for subtask in self.subtasks],
            "result": self.result,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary representation."""
        task = cls(
            task_id=data.get("task_id"),
            description=data.get("description", ""),
            user_id=data.get("user_id"),
            status=TaskStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data.get("updated_at")) if data.get("updated_at") else None,
            metadata=data.get("metadata", {}),
            parent_task_id=data.get("parent_task_id")
        )
        task.result = data.get("result")
        task.error = data.get("error")
        return task
    
    def update_status(self, status: TaskStatus) -> None:
        """Update the status of the task."""
        self.status = status
        self.updated_at = datetime.now()
        logger.info(f"Task {self.task_id} status updated to {status.value}")
    
    def add_subtask(self, subtask: 'Task') -> None:
        """Add a subtask to this task."""
        subtask.parent_task_id = self.task_id
        self.subtasks.append(subtask)
        logger.info(f"Subtask {subtask.task_id} added to task {self.task_id}")
    
    def set_result(self, result: Any) -> None:
        """Set the result of the task."""
        self.result = result
        self.update_status(TaskStatus.COMPLETED)
        logger.info(f"Task {self.task_id} completed with result")
    
    def set_error(self, error: str) -> None:
        """Set an error for the task."""
        self.error = error
        self.update_status(TaskStatus.FAILED)
        logger.error(f"Task {self.task_id} failed with error: {error}")

class TaskManager:
    """
    Manages the lifecycle of tasks in the system.
    """
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        logger.info("TaskManager initialized")
    
    def create_task(self, description: str, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Task:
        """Create a new task."""
        task = Task(description=description, user_id=user_id, metadata=metadata)
        self.tasks[task.task_id] = task
        logger.info(f"Task {task.task_id} created: {description}")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def update_task(self, task: Task) -> None:
        """Update a task in the manager."""
        self.tasks[task.task_id] = task
        logger.info(f"Task {task.task_id} updated")
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Task {task_id} deleted")
            return True
        return False
    
    def get_tasks_by_user(self, user_id: str) -> List[Task]:
        """Get all tasks for a specific user."""
        return [task for task in self.tasks.values() if task.user_id == user_id]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status."""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return self.get_tasks_by_status(TaskStatus.PENDING)
    
    def get_running_tasks(self) -> List[Task]:
        """Get all running tasks."""
        return self.get_tasks_by_status(TaskStatus.RUNNING)
