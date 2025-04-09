"""
Code execution tool for running code in a sandboxed environment.
"""

import logging
import subprocess
import tempfile
import os
from typing import Dict, List, Optional, Any

from src.tools.base_tool import BaseTool
from src.config import SANDBOX_ENABLED, TOOL_TIMEOUT

logger = logging.getLogger(__name__)

class CodeExecutionTool(BaseTool):
    """
    Tool for executing code in a sandboxed environment.
    """
    def __init__(
        self,
        tool_id: Optional[str] = None,
        name: str = "CodeExecution",
        description: str = "Tool for executing code in a sandboxed environment",
        timeout: int = TOOL_TIMEOUT,
        sandbox_enabled: bool = SANDBOX_ENABLED
    ):
        super().__init__(
            tool_id=tool_id,
            name=name,
            description=description,
            metadata={"timeout": timeout, "sandbox_enabled": sandbox_enabled}
        )
        self.timeout = timeout
        self.sandbox_enabled = sandbox_enabled
        logger.info(f"CodeExecutionTool initialized with sandbox_enabled={sandbox_enabled}")
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute code with the provided parameters.
        
        Args:
            language: The programming language (python, javascript, bash)
            code: The code to execute
            
        Returns:
            Dictionary containing the execution results
        """
        super().execute(**kwargs)
        
        language = kwargs.get("language", "python")
        code = kwargs.get("code", "")
        
        if not code:
            return {"status": "error", "message": "Code is required"}
        
        if language == "python":
            return self._execute_python(code)
        elif language == "javascript":
            return self._execute_javascript(code)
        elif language == "bash":
            return self._execute_bash(code)
        else:
            return {"status": "error", "message": f"Unsupported language: {language}"}
    
    def _execute_python(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code.
        
        Args:
            code: The Python code to execute
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
                temp_file.write(code.encode("utf-8"))
                temp_file_path = temp_file.name
            
            # Execute the code
            command = ["python3", temp_file_path]
            result = self._run_command(command)
            
            # Clean up
            os.unlink(temp_file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing Python code: {e}")
            return {"status": "error", "message": str(e)}
    
    def _execute_javascript(self, code: str) -> Dict[str, Any]:
        """
        Execute JavaScript code using Node.js.
        
        Args:
            code: The JavaScript code to execute
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as temp_file:
                temp_file.write(code.encode("utf-8"))
                temp_file_path = temp_file.name
            
            # Execute the code
            command = ["node", temp_file_path]
            result = self._run_command(command)
            
            # Clean up
            os.unlink(temp_file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing JavaScript code: {e}")
            return {"status": "error", "message": str(e)}
    
    def _execute_bash(self, code: str) -> Dict[str, Any]:
        """
        Execute Bash code.
        
        Args:
            code: The Bash code to execute
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as temp_file:
                temp_file.write(code.encode("utf-8"))
                temp_file_path = temp_file.name
            
            # Make the script executable
            os.chmod(temp_file_path, 0o755)
            
            # Execute the code
            command = ["/bin/bash", temp_file_path]
            result = self._run_command(command)
            
            # Clean up
            os.unlink(temp_file_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing Bash code: {e}")
            return {"status": "error", "message": str(e)}
    
    def _run_command(self, command: List[str]) -> Dict[str, Any]:
        """
        Run a command in a subprocess.
        
        Args:
            command: The command to run
            
        Returns:
            Dictionary with command output
        """
        try:
            logger.info(f"Running command: {' '.join(command)}")
            
            # Run the command
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for the process to complete with timeout
            stdout, stderr = process.communicate(timeout=self.timeout)
            
            return {
                "status": "success" if process.returncode == 0 else "error",
                "stdout": stdout,
                "stderr": stderr,
                "returncode": process.returncode
            }
            
        except subprocess.TimeoutExpired:
            # Kill the process if it times out
            process.kill()
            stdout, stderr = process.communicate()
            
            return {
                "status": "error",
                "message": f"Command timed out after {self.timeout} seconds",
                "stdout": stdout,
                "stderr": stderr,
                "returncode": -1
            }
            
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the tool parameters and return values.
        
        Returns:
            Dictionary with tool schema information
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "language": {
                    "type": "string",
                    "enum": ["python", "javascript", "bash"],
                    "description": "The programming language"
                },
                "code": {
                    "type": "string",
                    "description": "The code to execute"
                }
            },
            "returns": {
                "status": {
                    "type": "string",
                    "description": "Status of the operation (success or error)"
                },
                "message": {
                    "type": "string",
                    "description": "Error message if status is error"
                },
                "stdout": {
                    "type": "string",
                    "description": "Standard output from the code execution"
                },
                "stderr": {
                    "type": "string",
                    "description": "Standard error from the code execution"
                },
                "returncode": {
                    "type": "integer",
                    "description": "Return code from the code execution"
                }
            }
        }
