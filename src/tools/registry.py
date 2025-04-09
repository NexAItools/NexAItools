"""
Tool registry for managing and accessing tools in the system.
"""

import logging
from typing import Dict, List, Optional, Any, Type

from src.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Registry for managing and accessing tools in the system.
    """
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        logger.info("ToolRegistry initialized")
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a tool with the registry.
        
        Args:
            tool: The tool instance to register
        """
        self.tools[tool.tool_id] = tool
        logger.info(f"Tool {tool.name} ({tool.tool_id}) registered")
    
    def get_tool(self, tool_id: str) -> Optional[BaseTool]:
        """
        Get a tool by ID.
        
        Args:
            tool_id: The ID of the tool to retrieve
            
        Returns:
            The tool instance if found, None otherwise
        """
        return self.tools.get(tool_id)
    
    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            name: The name of the tool to retrieve
            
        Returns:
            The first tool instance with the given name if found, None otherwise
        """
        for tool in self.tools.values():
            if tool.name == name:
                return tool
        return None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all registered tools.
        
        Returns:
            List of dictionaries with tool information
        """
        return [
            {
                "tool_id": tool.tool_id,
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools.values()
        ]
    
    def unregister_tool(self, tool_id: str) -> bool:
        """
        Unregister a tool from the registry.
        
        Args:
            tool_id: The ID of the tool to unregister
            
        Returns:
            True if the tool was unregistered, False otherwise
        """
        if tool_id in self.tools:
            tool = self.tools[tool_id]
            del self.tools[tool_id]
            logger.info(f"Tool {tool.name} ({tool_id}) unregistered")
            return True
        return False
    
    def get_tools_by_type(self, tool_type: Type[BaseTool]) -> List[BaseTool]:
        """
        Get all tools of a specific type.
        
        Args:
            tool_type: The type of tools to retrieve
            
        Returns:
            List of tools of the specified type
        """
        return [tool for tool in self.tools.values() if isinstance(tool, tool_type)]
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get schemas for all registered tools.
        
        Returns:
            List of tool schemas
        """
        return [tool.get_schema() for tool in self.tools.values()]
