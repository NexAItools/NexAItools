"""
Frontend components for the Open Source Manus AI system.
This module contains the React components for the web interface.
"""

import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Main App component
const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [tasks, setTasks] = useState([]);
  const [agents, setAgents] = useState([]);

  // Fetch initial data
  useEffect(() => {
    fetchTasks();
    fetchAgents();
  }, []);

  // Fetch tasks from the API
  const fetchTasks = async () => {
    try {
      const response = await axios.get('/api/tasks');
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  // Fetch agents from the API
  const fetchAgents = async () => {
    try {
      const response = await axios.get('/api/agents');
      setAgents(response.data);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  // Send a message to the AI
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/messages', {
        content: input,
        sender_id: 'user',
        message_type: 'user_input',
      });

      setMessages((prevMessages) => [
        ...prevMessages,
        {
          id: response.data.message_id,
          sender: 'ai',
          content: response.data.content,
          timestamp: response.data.created_at,
        },
      ]);

      // Refresh tasks after sending a message
      fetchTasks();
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          id: Date.now(),
          sender: 'system',
          content: 'Error: Could not send message. Please try again.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle input change
  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Ashus AI</h1>
        <p>An Open Source AI Assistant</p>
      </header>

      <div className="main-content">
        <div className="sidebar">
          <div className="tasks-section">
            <h2>Tasks</h2>
            <ul className="tasks-list">
              {tasks.map((task) => (
                <li key={task.task_id} className={`task-item ${task.status}`}>
                  <div className="task-header">
                    <span className="task-status">{task.status}</span>
                    <span className="task-date">
                      {new Date(task.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="task-description">{task.description}</div>
                </li>
              ))}
            </ul>
          </div>

          <div className="agents-section">
            <h2>Agents</h2>
            <ul className="agents-list">
              {agents.map((agent) => (
                <li key={agent.agent_id} className="agent-item">
                  <div className="agent-name">{agent.name}</div>
                  <div className="agent-status">
                    {agent.is_active ? 'Active' : 'Inactive'}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="chat-container">
          <div className="messages-container">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.sender}-message`}
              >
                <div className="message-content">{message.content}</div>
                <div className="message-timestamp">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message ai-message loading">
                <div className="loading-indicator">
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </div>
              </div>
            )}
          </div>

          <form className="input-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={handleInputChange}
              placeholder="Type your message here..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      </div>

      <footer className="app-footer">
        <p>© 2025 Ashus AI - Open Source AI Assistant</p>
      </footer>
    </div>
  );
};

export default App;
