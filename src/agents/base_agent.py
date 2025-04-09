"""
Base agent class that all specialized agents will inherit from.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any

from src.orchestration.message_router import Message, MessageType

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    """
    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or self.__class__.__name__
        self.description = description
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.last_active = self.created_at
        self.is_active = True
        self.message_router = None
        logger.info(f"Agent {self.name} ({self.agent_id}) initialized")
    
    def register_message_router(self, message_router) -> None:
        """
        Register a message router with the agent.
        
        Args:
            message_router: The message router instance
        """
        self.message_router = message_router
        self.message_router.subscribe(self.agent_id, self.handle_message)
        logger.info(f"Agent {self.name} registered with message router")
    
    def send_message(self, recipient_id: Optional[str], message_type: MessageType, content: Any, 
                    metadata: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None) -> Message:
        """
        Send a message to another agent or component.
        
        Args:
            recipient_id: ID of the recipient, or None for broadcast
            message_type: Type of the message
            content: Content of the message
            metadata: Additional metadata for the message
            correlation_id: Correlation ID for message threading
            
        Returns:
            The sent message
        """
        if not self.message_router:
            raise RuntimeError(f"Agent {self.name} has no message router registered")
        
        message = Message(
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            correlation_id=correlation_id
        )
        
        self.message_router.publish(message)
        self.last_active = datetime.now()
        return message
    
    @abstractmethod
    def handle_message(self, message: Message) -> None:
        """
        Handle an incoming message.
        
        Args:
            message: The message to handle
        """
        self.last_active = datetime.now()
        logger.debug(f"Agent {self.name} received message {message.message_id} from {message.sender_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dictionary with agent status information
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    def activate(self) -> None:
        """Activate the agent."""
        self.is_active = True
        logger.info(f"Agent {self.name} activated")
    
    def deactivate(self) -> None:
        """Deactivate the agent."""
        self.is_active = False
        logger.info(f"Agent {self.name} deactivated")
    
    def __str__(self) -> str:
        return f"{self.name} ({self.agent_id})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(agent_id='{self.agent_id}', name='{self.name}')"
