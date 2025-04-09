"""
Database models and persistence layer for the Open Source Manus AI system.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from src.config import DB_URL

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine and session
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TaskModel(Base):
    """SQLAlchemy model for tasks."""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True)
    description = Column(Text, nullable=False)
    user_id = Column(String, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    metadata = Column(Text, nullable=True)  # JSON string
    parent_task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    result = Column(Text, nullable=True)  # JSON string
    error = Column(Text, nullable=True)
    
    # Relationships
    subtasks = relationship("TaskModel", backref="parent_task", remote_side=[id])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "task_id": self.id,
            "description": self.description,
            "user_id": self.user_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": json.loads(self.metadata) if self.metadata else {},
            "parent_task_id": self.parent_task_id,
            "result": json.loads(self.result) if self.result else None,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskModel':
        """Create model from dictionary."""
        return cls(
            id=data.get("task_id"),
            description=data.get("description", ""),
            user_id=data.get("user_id"),
            status=data.get("status", "pending"),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data.get("updated_at")) if data.get("updated_at") else datetime.now(),
            metadata=json.dumps(data.get("metadata", {})) if data.get("metadata") else None,
            parent_task_id=data.get("parent_task_id"),
            result=json.dumps(data.get("result")) if data.get("result") is not None else None,
            error=data.get("error")
        )

class MessageModel(Base):
    """SQLAlchemy model for messages."""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    sender_id = Column(String, nullable=False)
    recipient_id = Column(String, nullable=True)
    message_type = Column(String, nullable=False)
    content = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    metadata = Column(Text, nullable=True)  # JSON string
    correlation_id = Column(String, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "message_id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type,
            "content": json.loads(self.content) if self.content else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": json.loads(self.metadata) if self.metadata else {},
            "correlation_id": self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageModel':
        """Create model from dictionary."""
        return cls(
            id=data.get("message_id"),
            sender_id=data.get("sender_id", ""),
            recipient_id=data.get("recipient_id"),
            message_type=data.get("message_type", "notification"),
            content=json.dumps(data.get("content")) if data.get("content") is not None else None,
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else datetime.now(),
            metadata=json.dumps(data.get("metadata", {})) if data.get("metadata") else None,
            correlation_id=data.get("correlation_id")
        )

class AgentModel(Base):
    """SQLAlchemy model for agents."""
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_active = Column(DateTime, nullable=False, default=datetime.now)
    is_active = Column(Boolean, nullable=False, default=True)
    metadata = Column(Text, nullable=True)  # JSON string
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "agent_id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "is_active": self.is_active,
            "metadata": json.loads(self.metadata) if self.metadata else {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentModel':
        """Create model from dictionary."""
        return cls(
            id=data.get("agent_id"),
            name=data.get("name", ""),
            description=data.get("description"),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else datetime.now(),
            last_active=datetime.fromisoformat(data.get("last_active")) if data.get("last_active") else datetime.now(),
            is_active=data.get("is_active", True),
            metadata=json.dumps(data.get("metadata", {})) if data.get("metadata") else None
        )

class ToolModel(Base):
    """SQLAlchemy model for tools."""
    __tablename__ = "tools"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_used = Column(DateTime, nullable=False, default=datetime.now)
    metadata = Column(Text, nullable=True)  # JSON string
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "tool_id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "metadata": json.loads(self.metadata) if self.metadata else {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolModel':
        """Create model from dictionary."""
        return cls(
            id=data.get("tool_id"),
            name=data.get("name", ""),
            description=data.get("description"),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else datetime.now(),
            last_used=datetime.fromisoformat(data.get("last_used")) if data.get("last_used") else datetime.now(),
            metadata=json.dumps(data.get("metadata", {})) if data.get("metadata") else None
        )

def init_db():
    """Initialize the database by creating all tables."""
    logger.info("Initializing database")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
