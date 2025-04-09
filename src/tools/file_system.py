"""
File system tool for interacting with the local file system.
"""

import logging
import os
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class FileSystemTool(BaseTool):
    """
    Tool for interacting with the local file system.
    """
    def __init__(
        self,
        tool_id: Optional[str] = None,
        name: str = "FileSystem",
        description: str = "Tool for interacting with the local file system",
        base_dir: Optional[str] = None
    ):
        super().__init__(
            tool_id=tool_id,
            name=name,
            description=description,
            metadata={"base_dir": base_dir}
        )
        self.base_dir = Path(base_dir) if base_dir else None
        logger.info(f"FileSystemTool initialized with base_dir: {self.base_dir}")
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the file system tool with the provided parameters.
        
        Args:
            action: The action to perform (read, write, list, exists, delete, copy, move)
            path: The file or directory path
            content: The content to write (for write action)
            destination: The destination path (for copy and move actions)
            
        Returns:
            Dictionary containing the execution results
        """
        super().execute(**kwargs)
        
        action = kwargs.get("action", "list")
        path = kwargs.get("path", "")
        
        # Resolve path relative to base_dir if set
        if self.base_dir and not os.path.isabs(path):
            full_path = self.base_dir / path
        else:
            full_path = Path(path)
        
        # Validate path is within base_dir if set
        if self.base_dir and not str(full_path).startswith(str(self.base_dir)):
            return {"status": "error", "message": f"Path {path} is outside the allowed base directory"}
        
        if action == "read":
            return self._read_file(full_path)
        elif action == "write":
            return self._write_file(full_path, kwargs.get("content", ""))
        elif action == "list":
            return self._list_directory(full_path)
        elif action == "exists":
            return self._check_exists(full_path)
        elif action == "delete":
            return self._delete_path(full_path)
        elif action == "copy":
            destination = kwargs.get("destination", "")
            if not destination:
                return {"status": "error", "message": "Destination path is required for copy action"}
            
            # Resolve destination path
            if self.base_dir and not os.path.isabs(destination):
                full_destination = self.base_dir / destination
            else:
                full_destination = Path(destination)
            
            # Validate destination is within base_dir if set
            if self.base_dir and not str(full_destination).startswith(str(self.base_dir)):
                return {"status": "error", "message": f"Destination {destination} is outside the allowed base directory"}
            
            return self._copy_path(full_path, full_destination)
        elif action == "move":
            destination = kwargs.get("destination", "")
            if not destination:
                return {"status": "error", "message": "Destination path is required for move action"}
            
            # Resolve destination path
            if self.base_dir and not os.path.isabs(destination):
                full_destination = self.base_dir / destination
            else:
                full_destination = Path(destination)
            
            # Validate destination is within base_dir if set
            if self.base_dir and not str(full_destination).startswith(str(self.base_dir)):
                return {"status": "error", "message": f"Destination {destination} is outside the allowed base directory"}
            
            return self._move_path(full_path, full_destination)
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}
    
    def _read_file(self, path: Path) -> Dict[str, Any]:
        """
        Read a file.
        
        Args:
            path: Path to the file
            
        Returns:
            Dictionary with file content
        """
        try:
            if not path.exists():
                return {"status": "error", "message": f"File {path} does not exist"}
            
            if not path.is_file():
                return {"status": "error", "message": f"{path} is not a file"}
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            return {
                "status": "success",
                "path": str(path),
                "content": content,
                "size": path.stat().st_size,
                "modified": path.stat().st_mtime
            }
            
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _write_file(self, path: Path, content: str) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            path: Path to the file
            content: Content to write
            
        Returns:
            Dictionary with write status
        """
        try:
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return {
                "status": "success",
                "path": str(path),
                "size": path.stat().st_size,
                "modified": path.stat().st_mtime
            }
            
        except Exception as e:
            logger.error(f"Error writing to file {path}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _list_directory(self, path: Path) -> Dict[str, Any]:
        """
        List contents of a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            Dictionary with directory contents
        """
        try:
            if not path.exists():
                return {"status": "error", "message": f"Directory {path} does not exist"}
            
            if not path.is_dir():
                return {"status": "error", "message": f"{path} is not a directory"}
            
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": item.stat().st_mtime
                })
            
            return {
                "status": "success",
                "path": str(path),
                "items": items,
                "count": len(items)
            }
            
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _check_exists(self, path: Path) -> Dict[str, Any]:
        """
        Check if a file or directory exists.
        
        Args:
            path: Path to check
            
        Returns:
            Dictionary with existence status
        """
        try:
            exists = path.exists()
            
            result = {
                "status": "success",
                "path": str(path),
                "exists": exists
            }
            
            if exists:
                result.update({
                    "type": "directory" if path.is_dir() else "file",
                    "size": path.stat().st_size if path.is_file() else None,
                    "modified": path.stat().st_mtime
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking existence of {path}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _delete_path(self, path: Path) -> Dict[str, Any]:
        """
        Delete a file or directory.
        
        Args:
            path: Path to delete
            
        Returns:
            Dictionary with deletion status
        """
        try:
            if not path.exists():
                return {"status": "error", "message": f"Path {path} does not exist"}
            
            is_dir = path.is_dir()
            
            if is_dir:
                shutil.rmtree(path)
            else:
                path.unlink()
            
            return {
                "status": "success",
                "path": str(path),
                "type": "directory" if is_dir else "file"
            }
            
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _copy_path(self, source: Path, destination: Path) -> Dict[str, Any]:
        """
        Copy a file or directory.
        
        Args:
            source: Source path
            destination: Destination path
            
        Returns:
            Dictionary with copy status
        """
        try:
            if not source.exists():
                return {"status": "error", "message": f"Source {source} does not exist"}
            
            is_dir = source.is_dir()
            
            # Create parent directories if they don't exist
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            if is_dir:
                if destination.exists():
                    return {"status": "error", "message": f"Destination directory {destination} already exists"}
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            
            return {
                "status": "success",
                "source": str(source),
                "destination": str(destination),
                "type": "directory" if is_dir else "file"
            }
            
        except Exception as e:
            logger.error(f"Error copying {source} to {destination}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _move_path(self, source: Path, destination: Path) -> Dict[str, Any]:
        """
        Move a file or directory.
        
        Args:
            source: Source path
            destination: Destination path
            
        Returns:
            Dictionary with move status
        """
        try:
            if not source.exists():
                return {"status": "error", "message": f"Source {source} does not exist"}
            
            is_dir = source.is_dir()
            
            # Create parent directories if they don't exist
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source), str(destination))
            
            return {
                "status": "success",
                "source": str(source),
                "destination": str(destination),
                "type": "directory" if is_dir else "file"
            }
            
        except Exception as e:
            logger.error(f"Error moving {source} to {destination}: {e}")
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
                "action": {
                    "type": "string",
                    "enum": ["read", "write", "list", "exists", "delete", "copy", "move"],
                    "description": "The action to perform"
                },
                "path": {
                    "type": "string",
                    "description": "The file or directory path"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write (for write action)"
                },
                "destination": {
                    "type": "string",
                    "description": "The destination path (for copy and move actions)"
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
                "path": {
                    "type": "string",
                    "description": "Path of the file or directory"
                },
                "content": {
                    "type": "string",
                    "description": "Content of the file (for read action)"
                },
                "items": {
                    "type": "array",
                    "description": "List of items in a directory (for list action)"
                },
                "exists": {
                    "type": "boolean",
                    "description": "Whether the file or directory exists (for exists action)"
                }
            }
        }
