"""
Main entry point for the Open Source Manus AI application.
"""

import logging
import sys
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).resolve().parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from src.config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Main function to initialize and run the Open Source Manus AI system.
    """
    logger.info("Starting Open Source Manus AI system")
    
    try:
        # Import components here to avoid circular imports
        from src.orchestration.task_manager import TaskManager
        from src.agents.executor import ExecutorAgent
        from src.api.server import start_api_server
        
        # Initialize the system
        logger.info("Initializing system components")
        task_manager = TaskManager()
        executor_agent = ExecutorAgent(task_manager)
        
        # Start the API server
        logger.info("Starting API server")
        start_api_server()
        
    except Exception as e:
        logger.error(f"Error starting the system: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
