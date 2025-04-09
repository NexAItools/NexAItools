// Main JavaScript file for the Open Source Manus AI web interface

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatContainer = document.getElementById('chatContainer');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const fileUpload = document.getElementById('fileUpload');
    const uploadButton = document.getElementById('uploadButton');
    const taskList = document.getElementById('taskList');
    const navLinks = document.querySelectorAll('.sidebar-link');
    const contentSections = document.querySelectorAll('.content-section');

    // API Endpoints
    const API_URL = 'http://localhost:8000';
    const TASKS_ENDPOINT = `${API_URL}/tasks`;

    // Initialize the UI
    initializeUI();

    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    uploadButton.addEventListener('click', function() {
        fileUpload.click();
    });

    fileUpload.addEventListener('change', uploadFile);

    // Navigation
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-target');
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Show target section
            contentSections.forEach(section => {
                section.style.display = 'none';
            });
            document.getElementById(targetId).style.display = 'block';
        });
    });

    // Functions
    function initializeUI() {
        // Scroll chat to bottom
        scrollChatToBottom();
        
        // Load tasks
        fetchTasks();
        
        // Set up polling for task updates
        setInterval(fetchTasks, 5000);
    }

    function scrollChatToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function sendMessage() {
        const message = messageInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Clear input
        messageInput.value = '';
        
        // Add typing indicator
        addTypingIndicator();
        
        // Send message to API
        fetch(`${API_URL}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                description: message,
                metadata: {
                    source: 'web_ui',
                    type: 'chat'
                }
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add AI response to chat
            addMessageToChat('ai', 'I\'ve started working on your request. You can track the progress in the Tasks panel.');
            
            // Refresh task list
            fetchTasks();
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessageToChat('ai', 'Sorry, there was an error processing your request. Please try again.');
        });
    }

    function addMessageToChat(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = sender === 'user' ? 'user-message' : 'ai-message';
        messageDiv.textContent = content;
        
        const messageContainer = document.querySelector('.message-container');
        messageContainer.appendChild(messageDiv);
        
        scrollChatToBottom();
    }

    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'ai-message typing-message';
        typingDiv.innerHTML = `
            <div>
                <div class="typing-indicator"></div>
                <div class="typing-indicator" style="animation-delay: 0.2s"></div>
                <div class="typing-indicator" style="animation-delay: 0.4s"></div>
            </div>
        `;
        
        const messageContainer = document.querySelector('.message-container');
        messageContainer.appendChild(typingDiv);
        
        scrollChatToBottom();
    }

    function removeTypingIndicator() {
        const typingMessage = document.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }

    function uploadFile() {
        const file = fileUpload.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        addMessageToChat('user', `Uploading file: ${file.name}`);
        addTypingIndicator();
        
        // Upload file to API
        fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator();
            addMessageToChat('ai', `File uploaded successfully. What would you like me to do with ${file.name}?`);
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessageToChat('ai', 'Sorry, there was an error uploading your file. Please try again.');
        });
    }

    function fetchTasks() {
        fetch(TASKS_ENDPOINT)
        .then(response => response.json())
        .then(data => {
            updateTaskList(data.tasks);
        })
        .catch(error => {
            console.error('Error fetching tasks:', error);
        });
    }

    function updateTaskList(tasks) {
        // Clear current tasks
        taskList.innerHTML = '';
        
        // Add tasks to list
        tasks.forEach(task => {
            const taskCard = createTaskCard(task);
            taskList.appendChild(taskCard);
        });
        
        // If no tasks, show message
        if (tasks.length === 0) {
            const noTasksMessage = document.createElement('p');
            noTasksMessage.className = 'text-muted text-center my-4';
            noTasksMessage.textContent = 'No tasks yet. Start a conversation to create tasks.';
            taskList.appendChild(noTasksMessage);
        }
    }

    function createTaskCard(task) {
        const taskCard = document.createElement('div');
        taskCard.className = 'task-card card';
        taskCard.setAttribute('data-task-id', task.task_id);
        
        let statusClass = '';
        switch (task.status) {
            case 'pending':
                statusClass = 'status-pending';
                break;
            case 'running':
                statusClass = 'status-running';
                break;
            case 'completed':
                statusClass = 'status-completed';
                break;
            case 'failed':
                statusClass = 'status-failed';
                break;
            default:
                statusClass = 'status-pending';
        }
        
        taskCard.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <h6 class="card-title mb-0">${task.description.length > 30 ? task.description.substring(0, 30) + '...' : task.description}</h6>
                    <span class="task-status ${statusClass}">${task.status}</span>
                </div>
                <p class="card-text text-muted small mt-2">${task.description}</p>
                ${task.status === 'running' ? `
                <div class="progress mt-2" style="height: 5px;">
                    <div class="progress-bar" role="progressbar" style="width: 65%;" aria-valuenow="65" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                ` : ''}
            </div>
        `;
        
        // Add click event to view task details
        taskCard.addEventListener('click', function() {
            viewTaskDetails(task.task_id);
        });
        
        return taskCard;
    }

    function viewTaskDetails(taskId) {
        fetch(`${TASKS_ENDPOINT}/${taskId}`)
        .then(response => response.json())
        .then(task => {
            // Show task details modal
            const modal = new bootstrap.Modal(document.getElementById('taskDetailsModal'));
            
            document.getElementById('taskDetailsTitle').textContent = task.description;
            document.getElementById('taskDetailsStatus').textContent = task.status;
            document.getElementById('taskDetailsStatus').className = `task-status status-${task.status}`;
            document.getElementById('taskDetailsCreated').textContent = new Date(task.created_at).toLocaleString();
            document.getElementById('taskDetailsUpdated').textContent = new Date(task.updated_at).toLocaleString();
            
            const resultContainer = document.getElementById('taskDetailsResult');
            if (task.result) {
                resultContainer.textContent = typeof task.result === 'object' ? 
                    JSON.stringify(task.result, null, 2) : task.result;
            } else {
                resultContainer.textContent = 'No results yet';
            }
            
            const errorContainer = document.getElementById('taskDetailsError');
            if (task.error) {
                errorContainer.textContent = task.error;
                errorContainer.parentElement.style.display = 'block';
            } else {
                errorContainer.parentElement.style.display = 'none';
            }
            
            modal.show();
        })
        .catch(error => {
            console.error('Error fetching task details:', error);
        });
    }
});
