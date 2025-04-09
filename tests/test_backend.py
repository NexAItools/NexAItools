"""
Test script for the Ashus AI backend functionality.
This script tests the core components of the backend system.
"""

import unittest
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).resolve().parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from src.agents.base_agent import BaseAgent
from src.agents.executor import ExecutorAgent
from src.tools.base_tool import BaseTool
from src.tools.code_execution import CodeExecutionTool
from src.tools.file_system import FileSystemTool
from src.tools.web_browser import WebBrowserTool
from src.orchestration.task_manager import TaskManager, Task, TaskStatus
from src.orchestration.agent_manager import AgentManager
from src.orchestration.message_router import MessageRouter, Message
from src.tools.registry import ToolRegistry

class TestBackendFunctionality(unittest.TestCase):
    """Test cases for the backend functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task_manager = TaskManager()
        self.agent_manager = AgentManager()
        self.tool_registry = ToolRegistry()
        self.message_router = MessageRouter()
    
    def test_task_creation(self):
        """Test task creation and status updates."""
        # Create a task
        task = self.task_manager.create_task(
            description="Test task",
            user_id="test_user",
            metadata={"test_key": "test_value"}
        )
        
        # Check task properties
        self.assertIsNotNone(task.task_id)
        self.assertEqual(task.description, "Test task")
        self.assertEqual(task.user_id, "test_user")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.metadata.get("test_key"), "test_value")
        
        # Update task status
        task.update_status(TaskStatus.RUNNING)
        self.assertEqual(task.status, TaskStatus.RUNNING)
        
        # Set task result
        task.set_result({"result_key": "result_value"})
        self.assertEqual(task.status, TaskStatus.COMPLETED)
        self.assertEqual(task.result.get("result_key"), "result_value")
    
    def test_subtask_creation(self):
        """Test subtask creation and parent-child relationships."""
        # Create parent task
        parent_task = self.task_manager.create_task(description="Parent task")
        
        # Create subtask
        subtask = Task(description="Subtask")
        parent_task.add_subtask(subtask)
        
        # Check relationships
        self.assertEqual(subtask.parent_task_id, parent_task.task_id)
        self.assertIn(subtask, parent_task.subtasks)
    
    def test_agent_registration(self):
        """Test agent registration and retrieval."""
        # Create and register an agent
        agent = BaseAgent(name="Test Agent")
        self.agent_manager.register_agent(agent.agent_id, agent)
        
        # Retrieve the agent
        retrieved_agent = self.agent_manager.get_agent(agent.agent_id)
        
        # Check agent properties
        self.assertEqual(retrieved_agent.agent_id, agent.agent_id)
        self.assertEqual(retrieved_agent.name, "Test Agent")
        
        # List agents
        agent_ids = self.agent_manager.list_agents()
        self.assertIn(agent.agent_id, agent_ids)
        
        # Unregister agent
        result = self.agent_manager.unregister_agent(agent.agent_id)
        self.assertTrue(result)
        
        # Check agent is no longer registered
        self.assertIsNone(self.agent_manager.get_agent(agent.agent_id))
    
    def test_tool_registration(self):
        """Test tool registration and retrieval."""
        # Create and register tools
        file_tool = FileSystemTool()
        code_tool = CodeExecutionTool()
        
        self.tool_registry.register_tool(file_tool)
        self.tool_registry.register_tool(code_tool)
        
        # Retrieve tools
        retrieved_file_tool = self.tool_registry.get_tool(file_tool.tool_id)
        retrieved_code_tool = self.tool_registry.get_tool_by_name("CodeExecution")
        
        # Check tool properties
        self.assertEqual(retrieved_file_tool.tool_id, file_tool.tool_id)
        self.assertEqual(retrieved_code_tool.name, "CodeExecution")
        
        # List tools
        tools_list = self.tool_registry.list_tools()
        self.assertEqual(len(tools_list), 2)
        
        # Get tool schemas
        schemas = self.tool_registry.get_tool_schemas()
        self.assertEqual(len(schemas), 2)
        
        # Unregister tool
        result = self.tool_registry.unregister_tool(file_tool.tool_id)
        self.assertTrue(result)
        
        # Check tool is no longer registered
        self.assertIsNone(self.tool_registry.get_tool(file_tool.tool_id))
    
    def test_message_routing(self):
        """Test message routing functionality."""
        # Create a message
        message = Message(
            content="Test message",
            sender_id="user_1",
            recipient_id="agent_1",
            message_type="text"
        )
        
        # Convert to dict and back
        message_dict = message.to_dict()
        reconstructed_message = Message.from_dict(message_dict)
        
        # Check message properties
        self.assertEqual(reconstructed_message.content, "Test message")
        self.assertEqual(reconstructed_message.sender_id, "user_1")
        self.assertEqual(reconstructed_message.recipient_id, "agent_1")
        self.assertEqual(reconstructed_message.message_type, "text")

if __name__ == "__main__":
    unittest.main()
