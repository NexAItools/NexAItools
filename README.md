# NexAItools - Open Source AI Assistant

NexAItools is an open-source AI system with capabilities similar to Manus AI, featuring a multi-agent architecture, tool integration, and web/CLI interfaces.

## Features

- Multi-agent architecture for complex task handling
- Tool integration for code execution, file system operations, and web browsing
- Web interface for user interaction
- API for programmatic access
- Task management and tracking
- Message routing between agents

## System Architecture

NexAItools is built with a modular architecture consisting of the following components:

1. **Agents**: Specialized AI agents that perform specific tasks
   - Executor Agent: Coordinates execution of tasks
   - Base Agent: Abstract class for all agents

2. **Tools**: Utilities that agents can use to interact with the environment
   - Code Execution Tool: Runs code in various languages
   - File System Tool: Manages files and directories
   - Web Browser Tool: Accesses and interacts with web pages

3. **Orchestration**: Components that manage the system's operation
   - Task Manager: Handles task creation, assignment, and tracking
   - Agent Manager: Manages agent lifecycle and coordination
   - Message Router: Routes messages between users and agents

4. **API**: Interfaces for external interaction
   - REST API: HTTP endpoints for web and programmatic access
   - CLI: Command-line interface for local interaction

5. **Frontend**: User interface components
   - Web Interface: React-based UI for interacting with the system

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 14 or higher
- PostgreSQL (optional, for production use)

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/NexAItools/NexAItools.git
   cd NexAItools
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file in the project root):
   ```
   API_HOST=0.0.0.0
   API_PORT=8000
   API_DEBUG=True
   DB_TYPE=sqlite  # Use postgresql for production
   DB_NAME=nexaitools.db
   LOG_LEVEL=INFO
   ```

5. Initialize the database:
   ```
   python -m src.persistence.database
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd src/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Build the frontend:
   ```
   npm run build
   ```

## Usage

### Starting the System

1. Start the backend server:
   ```
   python -m src.main
   ```

2. Access the web interface at `http://localhost:8000`

### API Endpoints

- `GET /api/tasks`: List all tasks
- `POST /api/tasks`: Create a new task
- `GET /api/tasks/{task_id}`: Get a specific task
- `PUT /api/tasks/{task_id}`: Update a task
- `GET /api/messages`: List messages
- `POST /api/messages`: Send a message
- `GET /api/agents`: List all agents
- `GET /api/status`: Get system status

## Development

### Running Tests

1. Backend tests:
   ```
   python -m unittest discover tests
   ```

2. Frontend tests:
   ```
   cd src/frontend
   npm test
   ```

### Project Structure

```
NexAItools/
├── data/                  # Data storage
├── logs/                  # Log files
├── src/                   # Source code
│   ├── agents/            # Agent implementations
│   ├── api/               # API endpoints
│   ├── frontend/          # Frontend components
│   ├── orchestration/     # System orchestration
│   ├── persistence/       # Database models
│   ├── tools/             # Tool implementations
│   ├── config.py          # Configuration
│   └── main.py            # Entry point
├── tests/                 # Test scripts
├── LICENSE                # License information
├── COPYRIGHT.md           # Copyright documentation
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Copyright

All copyright and intellectual property rights for the NexAItools project are owned by you. See [COPYRIGHT.md](COPYRIGHT.md) for detailed information.
