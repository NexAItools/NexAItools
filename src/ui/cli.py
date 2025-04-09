#!/usr/bin/env python3
"""
Command-line interface for the Open Source Manus AI system.
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Optional, Any

import requests

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import API_HOST, API_PORT

# API URL
API_URL = f"http://{API_HOST}:{API_PORT}"

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}\n")

def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}{text}{Colors.ENDC}")

def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}{text}{Colors.ENDC}")

def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}{text}{Colors.ENDC}")

def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}{text}{Colors.ENDC}")

def create_task(description: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a new task.
    
    Args:
        description: Task description
        metadata: Optional metadata
        
    Returns:
        Task data
    """
    url = f"{API_URL}/tasks"
    data = {
        "description": description,
        "metadata": metadata or {"source": "cli"}
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print_error(f"Error creating task: {e}")
        sys.exit(1)

def get_tasks(user_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get tasks, optionally filtered by user ID or status.
    
    Args:
        user_id: Optional user ID filter
        status: Optional status filter
        
    Returns:
        List of tasks
    """
    url = f"{API_URL}/tasks"
    params = {}
    if user_id:
        params["user_id"] = user_id
    if status:
        params["status"] = status
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()["tasks"]
    except requests.exceptions.RequestException as e:
        print_error(f"Error getting tasks: {e}")
        sys.exit(1)

def get_task(task_id: str) -> Dict[str, Any]:
    """
    Get a specific task by ID.
    
    Args:
        task_id: Task ID
        
    Returns:
        Task data
    """
    url = f"{API_URL}/tasks/{task_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print_error(f"Error getting task: {e}")
        sys.exit(1)

def delete_task(task_id: str) -> None:
    """
    Delete a task by ID.
    
    Args:
        task_id: Task ID
    """
    url = f"{API_URL}/tasks/{task_id}"
    
    try:
        response = requests.delete(url)
        response.raise_for_status()
        print_success(f"Task {task_id} deleted successfully")
    except requests.exceptions.RequestException as e:
        print_error(f"Error deleting task: {e}")
        sys.exit(1)

def print_task(task: Dict[str, Any], detailed: bool = False) -> None:
    """
    Print task information.
    
    Args:
        task: Task data
        detailed: Whether to print detailed information
    """
    status_color = Colors.BLUE
    if task["status"] == "completed":
        status_color = Colors.GREEN
    elif task["status"] == "failed":
        status_color = Colors.RED
    elif task["status"] == "running":
        status_color = Colors.YELLOW
    
    print(f"Task ID: {Colors.BOLD}{task['task_id']}{Colors.ENDC}")
    print(f"Description: {task['description']}")
    print(f"Status: {status_color}{task['status']}{Colors.ENDC}")
    print(f"Created: {task['created_at']}")
    print(f"Updated: {task['updated_at']}")
    
    if detailed:
        if task.get("user_id"):
            print(f"User ID: {task['user_id']}")
        
        if task.get("result"):
            print(f"\n{Colors.BOLD}Result:{Colors.ENDC}")
            if isinstance(task["result"], dict) or isinstance(task["result"], list):
                print(json.dumps(task["result"], indent=2))
            else:
                print(task["result"])
        
        if task.get("error"):
            print(f"\n{Colors.BOLD}Error:{Colors.ENDC}")
            print(f"{Colors.RED}{task['error']}{Colors.ENDC}")

def interactive_mode() -> None:
    """Start interactive mode."""
    print_header("Open Source Manus AI - Interactive Mode")
    print("Type 'help' for available commands or 'exit' to quit.")
    
    while True:
        try:
            user_input = input(f"\n{Colors.BOLD}manus> {Colors.ENDC}").strip()
            
            if user_input.lower() in ["exit", "quit", "q"]:
                break
            
            if user_input.lower() in ["help", "h", "?"]:
                print_info("Available commands:")
                print("  help - Show this help message")
                print("  exit - Exit the program")
                print("  tasks - List all tasks")
                print("  task <id> - Show details for a specific task")
                print("  create <description> - Create a new task")
                print("  delete <id> - Delete a task")
                print("  Any other input will be treated as a task description")
                continue
            
            if user_input.lower() == "tasks":
                tasks = get_tasks()
                if not tasks:
                    print_warning("No tasks found")
                    continue
                
                print_header("Tasks")
                for task in tasks:
                    print_task(task)
                    print("-" * 40)
                continue
            
            if user_input.lower().startswith("task "):
                task_id = user_input[5:].strip()
                task = get_task(task_id)
                print_header(f"Task Details: {task_id}")
                print_task(task, detailed=True)
                continue
            
            if user_input.lower().startswith("create "):
                description = user_input[7:].strip()
                task = create_task(description)
                print_success(f"Task created with ID: {task['task_id']}")
                continue
            
            if user_input.lower().startswith("delete "):
                task_id = user_input[7:].strip()
                delete_task(task_id)
                continue
            
            # Treat as task description
            print_info("Creating task...")
            task = create_task(user_input)
            print_success(f"Task created with ID: {task['task_id']}")
            
            # Wait for task to complete
            print_info("Waiting for task to complete...")
            while True:
                task = get_task(task['task_id'])
                if task['status'] in ['completed', 'failed']:
                    break
                time.sleep(1)
                print(".", end="", flush=True)
            
            print("\n")
            print_header("Task Result")
            print_task(task, detailed=True)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print_error(f"Error: {e}")

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Command-line interface for Open Source Manus AI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Interactive mode
    parser_interactive = subparsers.add_parser("interactive", help="Start interactive mode")
    
    # Create task
    parser_create = subparsers.add_parser("create", help="Create a new task")
    parser_create.add_argument("description", help="Task description")
    
    # List tasks
    parser_list = subparsers.add_parser("list", help="List tasks")
    parser_list.add_argument("--user", help="Filter by user ID")
    parser_list.add_argument("--status", help="Filter by status")
    
    # Get task
    parser_get = subparsers.add_parser("get", help="Get a specific task")
    parser_get.add_argument("task_id", help="Task ID")
    
    # Delete task
    parser_delete = subparsers.add_parser("delete", help="Delete a task")
    parser_delete.add_argument("task_id", help="Task ID")
    
    args = parser.parse_args()
    
    if args.command == "interactive" or not args.command:
        interactive_mode()
    elif args.command == "create":
        task = create_task(args.description)
        print_success(f"Task created with ID: {task['task_id']}")
    elif args.command == "list":
        tasks = get_tasks(user_id=args.user, status=args.status)
        if not tasks:
            print_warning("No tasks found")
            return
        
        print_header("Tasks")
        for task in tasks:
            print_task(task)
            print("-" * 40)
    elif args.command == "get":
        task = get_task(args.task_id)
        print_header(f"Task Details: {args.task_id}")
        print_task(task, detailed=True)
    elif args.command == "delete":
        delete_task(args.task_id)

if __name__ == "__main__":
    main()
