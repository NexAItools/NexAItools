"""
Agent Manager for coordinating different agents in the system.
"""

import logging
from typing import Dict, List, Optional, Any, Type

from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Manages the lifecycle and coordination of agents in the system.
    """
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        logger.info("AgentManager initialized")
    
    def register_agent(self, agent_id: str, agent: BaseAgent) -> None:
        """
        Register an agent with the manager.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: The agent instance to register
        """
        self.agents[agent_id] = agent
        logger.info(f"Agent {agent_id} registered")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve
            
        Returns:
            The agent instance if found, None otherwise
        """
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """
        List all registered agent IDs.
        
        Returns:
            List of agent IDs
        """
        return list(self.agents.keys())
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the manager.
        
        Args:
            agent_id: The ID of the agent to unregister
            
        Returns:
            True if the agent was unregistered, False otherwise
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent {agent_id} unregistered")
            return True
        return False
    
    def get_agent_by_type(self, agent_type: Type[BaseAgent]) -> List[BaseAgent]:
        """
        Get all agents of a specific type.
        
        Args:
            agent_type: The type of agents to retrieve
            
        Returns:
            List of agents of the specified type
        """
        return [agent for agent in self.agents.values() if isinstance(agent, agent_type)]
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            Dictionary with agent status information if found, None otherwise
        """
        agent = self.get_agent(agent_id)
        if agent:
            return agent.get_status()
        return None
