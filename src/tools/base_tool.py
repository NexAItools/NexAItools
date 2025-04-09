"""
Base tool class that all tools will inherit from.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """
    Abstract base class for all tools in the system.
    """
    def __init__(
        self,
        tool_id: Optional[str] = None,
        name: str = "",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.tool_id = tool_id or str(uuid.uuid4())
        self.name = name or self.__class__.__name__
        self.description = description
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.last_used = self.created_at
        logger.info(f"Tool {self.name} ({self.tool_id}) initialized")
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the provided parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Dictionary containing the execution results
        """
        self.last_used = datetime.now()
        logger.debug(f"Tool {self.name} executed with parameters: {kwargs}")
        return {"status": "not_implemented"}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the tool.
        
        Returns:
            Dictionary with tool status information
        """
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat(),
            "metadata": self.metadata
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the tool parameters and return values.
        
        Returns:
            Dictionary with tool schema information
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {},
            "returns": {}
        }
    
    def __str__(self) -> str:
        return f"{self.name} ({self.tool_id})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(tool_id='{self.tool_id}', name='{self.name}')"
