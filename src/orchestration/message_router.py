"""
Message Router for handling communication between agents and components.
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Enum representing the possible types of messages."""
    TASK = "task"
    RESULT = "result"
    ERROR = "error"
    STATUS = "status"
    COMMAND = "command"
    NOTIFICATION = "notification"

class Message:
    """
    Represents a message exchanged between agents and components.
    """
    def __init__(
        self,
        message_id: Optional[str] = None,
        sender_id: str = "",
        recipient_id: Optional[str] = None,
        message_type: MessageType = MessageType.NOTIFICATION,
        content: Any = None,
        created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        self.message_id = message_id or str(uuid.uuid4())
        self.sender_id = sender_id
        self.recipient_id = recipient_id  # None means broadcast
        self.message_type = message_type
        self.content = content
        self.created_at = created_at or datetime.now()
        self.metadata = metadata or {}
        self.correlation_id = correlation_id or self.message_id
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "correlation_id": self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary representation."""
        return cls(
            message_id=data.get("message_id"),
            sender_id=data.get("sender_id", ""),
            recipient_id=data.get("recipient_id"),
            message_type=MessageType(data.get("message_type", "notification")),
            content=data.get("content"),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None,
            metadata=data.get("metadata", {}),
            correlation_id=data.get("correlation_id")
        )

class MessageRouter:
    """
    Routes messages between agents and components in the system.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Message], None]]] = {}
        self.message_history: List[Message] = []
        self.max_history_size = 1000
        logger.info("MessageRouter initialized")
    
    def publish(self, message: Message) -> None:
        """
        Publish a message to subscribers.
        
        Args:
            message: The message to publish
        """
        # Store message in history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history_size:
            self.message_history.pop(0)
        
        # Determine recipients
        if message.recipient_id:
            # Direct message to specific recipient
            recipients = [message.recipient_id]
        else:
            # Broadcast message to all subscribers
            recipients = list(self.subscribers.keys())
        
        # Deliver message to recipients
        for recipient_id in recipients:
            if recipient_id in self.subscribers:
                for callback in self.subscribers[recipient_id]:
                    try:
                        callback(message)
                    except Exception as e:
                        logger.error(f"Error delivering message to {recipient_id}: {e}", exc_info=True)
        
        logger.debug(f"Message {message.message_id} published from {message.sender_id} to {recipients}")
    
    def subscribe(self, subscriber_id: str, callback: Callable[[Message], None]) -> None:
        """
        Subscribe to messages.
        
        Args:
            subscriber_id: Unique identifier for the subscriber
            callback: Function to call when a message is received
        """
        if subscriber_id not in self.subscribers:
            self.subscribers[subscriber_id] = []
        
        self.subscribers[subscriber_id].append(callback)
        logger.info(f"Subscriber {subscriber_id} registered")
    
    def unsubscribe(self, subscriber_id: str, callback: Optional[Callable[[Message], None]] = None) -> None:
        """
        Unsubscribe from messages.
        
        Args:
            subscriber_id: Unique identifier for the subscriber
            callback: Specific callback to unsubscribe, or None to unsubscribe all
        """
        if subscriber_id in self.subscribers:
            if callback:
                self.subscribers[subscriber_id] = [cb for cb in self.subscribers[subscriber_id] if cb != callback]
                if not self.subscribers[subscriber_id]:
                    del self.subscribers[subscriber_id]
                logger.info(f"Callback unsubscribed for {subscriber_id}")
            else:
                del self.subscribers[subscriber_id]
                logger.info(f"Subscriber {subscriber_id} unsubscribed")
    
    def get_message_history(self, limit: Optional[int] = None) -> List[Message]:
        """
        Get message history.
        
        Args:
            limit: Maximum number of messages to return, or None for all
            
        Returns:
            List of messages
        """
        if limit:
            return self.message_history[-limit:]
        return self.message_history.copy()
    
    def get_messages_by_correlation(self, correlation_id: str) -> List[Message]:
        """
        Get all messages with a specific correlation ID.
        
        Args:
            correlation_id: The correlation ID to filter by
            
        Returns:
            List of messages with the specified correlation ID
        """
        return [msg for msg in self.message_history if msg.correlation_id == correlation_id]
