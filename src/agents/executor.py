"""
Central Executor Agent that coordinates the overall execution of tasks.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple

import autogen
from autogen import Agent, AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

from src.config import DEFAULT_EXECUTOR_MODEL, AGENT_TIMEOUT
from src.orchestration.task_manager import Task, TaskManager, TaskStatus
from src.orchestration.message_router import Message, MessageType
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ExecutorAgent(BaseAgent):
    """
    Central Executor Agent that coordinates the execution of tasks and delegates to specialized agents.
    """
    def __init__(
        self,
        task_manager: TaskManager,
        agent_id: Optional[str] = None,
        name: str = "ExecutorAgent",
        description: str = "Central agent that coordinates task execution and delegates to specialized agents",
        model: str = DEFAULT_EXECUTOR_MODEL,
        timeout: int = AGENT_TIMEOUT
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            description=description,
            metadata={"model": model, "timeout": timeout}
        )
        self.task_manager = task_manager
        self.model = model
        self.timeout = timeout
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.agent_group = self._initialize_agent_group()
        logger.info(f"ExecutorAgent initialized with model {model}")
    
    def _initialize_agent_group(self) -> Tuple[GroupChat, GroupChatManager]:
        """
        Initialize the AutoGen agent group for task execution.
        
        Returns:
            Tuple of GroupChat and GroupChatManager
        """
        # Create the executor assistant agent
        executor_agent = AssistantAgent(
            name="executor",
            llm_config={
                "model": self.model,
                "temperature": 0.2,
                "config_list": [{"model": self.model}]
            },
            system_message="""You are the central executor agent responsible for coordinating task execution.
            Your role is to analyze tasks, create execution plans, and delegate subtasks to specialized agents.
            You should break down complex tasks into manageable steps and ensure all steps are completed successfully.
            """
        )
        
        # Create the planner agent
        planner_agent = AssistantAgent(
            name="planner",
            llm_config={
                "model": self.model,
                "temperature": 0.1,
                "config_list": [{"model": self.model}]
            },
            system_message="""You are the planner agent responsible for creating detailed execution plans.
            Your role is to analyze tasks and break them down into specific steps that can be executed by other agents.
            You should consider dependencies between steps and create a logical sequence of operations.
            """
        )
        
        # Create the tool-using agent
        tool_agent = AssistantAgent(
            name="tool_user",
            llm_config={
                "model": self.model,
                "temperature": 0.2,
                "config_list": [{"model": self.model}]
            },
            system_message="""You are the tool-using agent responsible for interacting with external tools and services.
            Your role is to execute operations using available tools based on the requirements of the task.
            You should report the results of tool operations back to the executor agent.
            """
        )
        
        # Create the knowledge agent
        knowledge_agent = AssistantAgent(
            name="knowledge",
            llm_config={
                "model": self.model,
                "temperature": 0.3,
                "config_list": [{"model": self.model}]
            },
            system_message="""You are the knowledge agent responsible for retrieving and providing information.
            Your role is to search for relevant information, provide context, and answer questions based on available data.
            You should ensure that information is accurate, relevant, and properly cited.
            """
        )
        
        # Create a user proxy agent to represent the task
        user_proxy = UserProxyAgent(
            name="task",
            human_input_mode="NEVER",
            code_execution_config={"use_docker": False},
            system_message="""You represent the task that needs to be executed.
            Your role is to provide the initial task description and any additional information requested by the agents.
            You should also validate the final results of the task execution.
            """
        )
        
        # Create the group chat
        group_chat = GroupChat(
            agents=[user_proxy, executor_agent, planner_agent, tool_agent, knowledge_agent],
            messages=[],
            max_round=50
        )
        
        # Create the group chat manager
        manager = GroupChatManager(
            groupchat=group_chat,
            llm_config={
                "model": self.model,
                "temperature": 0.2,
                "config_list": [{"model": self.model}]
            }
        )
        
        return group_chat, manager
    
    def handle_message(self, message: Message) -> None:
        """
        Handle incoming messages.
        
        Args:
            message: The message to handle
        """
        super().handle_message(message)
        
        if message.message_type == MessageType.TASK:
            # Handle new task assignment
            task_id = message.content.get("task_id")
            if task_id:
                self._process_task(task_id)
        
        elif message.message_type == MessageType.RESULT:
            # Handle subtask result
            task_id = message.content.get("task_id")
            result = message.content.get("result")
            if task_id and task_id in self.active_tasks:
                self._handle_subtask_result(task_id, result, message.sender_id)
        
        elif message.message_type == MessageType.ERROR:
            # Handle error in subtask
            task_id = message.content.get("task_id")
            error = message.content.get("error")
            if task_id and task_id in self.active_tasks:
                self._handle_subtask_error(task_id, error, message.sender_id)
    
    def execute_task(self, task: Task) -> None:
        """
        Execute a task using the agent group.
        
        Args:
            task: The task to execute
        """
        logger.info(f"ExecutorAgent starting execution of task {task.task_id}: {task.description}")
        
        # Update task status
        task.update_status(TaskStatus.RUNNING)
        self.task_manager.update_task(task)
        
        # Store task in active tasks
        self.active_tasks[task.task_id] = {
            "task": task,
            "subtasks": {},
            "chat_history": []
        }
        
        try:
            # Initialize the chat with the task description
            user_proxy = next(agent for agent in self.agent_group[0].agents if agent.name == "task")
            user_proxy.initiate_chat(
                self.agent_group[1],
                message=f"Task: {task.description}\nMetadata: {json.dumps(task.metadata)}"
            )
            
            # Extract the results from the chat
            chat_history = self.agent_group[0].messages
            self.active_tasks[task.task_id]["chat_history"] = chat_history
            
            # Process the final result
            final_messages = [msg for msg in chat_history if msg["role"] == "assistant" and msg["name"] == "executor"]
            if final_messages:
                final_result = final_messages[-1]["content"]
                task.set_result(final_result)
            else:
                task.set_error("No final result was produced by the executor agent")
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {e}", exc_info=True)
            task.set_error(f"Error during execution: {str(e)}")
        
        # Clean up
        self.task_manager.update_task(task)
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
    
    def _process_task(self, task_id: str) -> None:
        """
        Process a task by ID.
        
        Args:
            task_id: ID of the task to process
        """
        task = self.task_manager.get_task(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        self.execute_task(task)
    
    def _handle_subtask_result(self, task_id: str, result: Any, sender_id: str) -> None:
        """
        Handle the result of a subtask.
        
        Args:
            task_id: ID of the parent task
            result: Result of the subtask
            sender_id: ID of the agent that sent the result
        """
        if task_id not in self.active_tasks:
            logger.warning(f"Received result for unknown task {task_id}")
            return
        
        logger.info(f"Received result for task {task_id} from {sender_id}")
        
        # Update subtask status
        if "subtasks" in self.active_tasks[task_id] and sender_id in self.active_tasks[task_id]["subtasks"]:
            self.active_tasks[task_id]["subtasks"][sender_id]["status"] = "completed"
            self.active_tasks[task_id]["subtasks"][sender_id]["result"] = result
        
        # Check if all subtasks are completed
        all_completed = all(
            subtask["status"] == "completed" 
            for subtask in self.active_tasks[task_id]["subtasks"].values()
        )
        
        if all_completed:
            # All subtasks completed, finalize the task
            self._finalize_task(task_id)
    
    def _handle_subtask_error(self, task_id: str, error: str, sender_id: str) -> None:
        """
        Handle an error in a subtask.
        
        Args:
            task_id: ID of the parent task
            error: Error message
            sender_id: ID of the agent that sent the error
        """
        if task_id not in self.active_tasks:
            logger.warning(f"Received error for unknown task {task_id}")
            return
        
        logger.error(f"Received error for task {task_id} from {sender_id}: {error}")
        
        # Update subtask status
        if "subtasks" in self.active_tasks[task_id] and sender_id in self.active_tasks[task_id]["subtasks"]:
            self.active_tasks[task_id]["subtasks"][sender_id]["status"] = "failed"
            self.active_tasks[task_id]["subtasks"][sender_id]["error"] = error
        
        # Decide whether to retry, use alternative approach, or fail the task
        # For now, we'll just fail the task
        task = self.active_tasks[task_id]["task"]
        task.set_error(f"Subtask executed by {sender_id} failed: {error}")
        self.task_manager.update_task(task)
        
        # Clean up
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
    
    def _finalize_task(self, task_id: str) -> None:
        """
        Finalize a task by aggregating subtask results.
        
        Args:
            task_id: ID of the task to finalize
        """
        if task_id not in self.active_tasks:
            logger.warning(f"Cannot finalize unknown task {task_id}")
            return
        
        logger.info(f"Finalizing task {task_id}")
        
        task = self.active_tasks[task_id]["task"]
        subtasks = self.active_tasks[task_id]["subtasks"]
        
        # Aggregate results from subtasks
        results = {
            agent_id: subtask["result"]
            for agent_id, subtask in subtasks.items()
            if subtask["status"] == "completed"
        }
        
        # Set the final result
        task.set_result(results)
        self.task_manager.update_task(task)
        
        # Clean up
        del self.active_tasks[task_id]
        
        logger.info(f"Task {task_id} completed successfully")
