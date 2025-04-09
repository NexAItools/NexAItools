"""
Test script for the Ashus AI frontend functionality.
This script tests the React components of the frontend system.
"""

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import App from '../src/frontend/components/App';

// Mock axios
jest.mock('axios');

describe('Frontend Component Tests', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders the application header', () => {
    render(<App />);
    const headerElement = screen.getByText(/Ashus AI/i);
    expect(headerElement).toBeInTheDocument();
    
    const subtitleElement = screen.getByText(/An Open Source AI Assistant/i);
    expect(subtitleElement).toBeInTheDocument();
  });

  test('renders the input form', () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Type your message here/i);
    expect(inputElement).toBeInTheDocument();
    
    const sendButton = screen.getByText(/Send/i);
    expect(sendButton).toBeInTheDocument();
    expect(sendButton).toBeDisabled(); // Button should be disabled when input is empty
  });

  test('enables send button when input has text', () => {
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Type your message here/i);
    const sendButton = screen.getByText(/Send/i);
    
    // Initially button should be disabled
    expect(sendButton).toBeDisabled();
    
    // Type in the input
    fireEvent.change(inputElement, { target: { value: 'Hello Ashus AI' } });
    
    // Button should now be enabled
    expect(sendButton).not.toBeDisabled();
  });

  test('sends message and displays response', async () => {
    // Mock API responses
    axios.post.mockResolvedValueOnce({
      data: {
        message_id: '123',
        content: 'Hello! How can I help you today?',
        created_at: new Date().toISOString(),
      },
    });
    
    axios.get.mockResolvedValue({ data: [] }); // Mock empty tasks and agents lists
    
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Type your message here/i);
    const sendButton = screen.getByText(/Send/i);
    
    // Type and send a message
    fireEvent.change(inputElement, { target: { value: 'Hello Ashus AI' } });
    fireEvent.click(sendButton);
    
    // Check that user message is displayed
    expect(screen.getByText('Hello Ashus AI')).toBeInTheDocument();
    
    // Wait for and check AI response
    await waitFor(() => {
      expect(screen.getByText('Hello! How can I help you today?')).toBeInTheDocument();
    });
    
    // Check that input is cleared after sending
    expect(inputElement.value).toBe('');
  });

  test('displays tasks from API', async () => {
    // Mock tasks API response
    axios.get.mockImplementation((url) => {
      if (url === '/api/tasks') {
        return Promise.resolve({
          data: [
            {
              task_id: '1',
              description: 'Test task 1',
              status: 'completed',
              created_at: new Date().toISOString(),
            },
            {
              task_id: '2',
              description: 'Test task 2',
              status: 'running',
              created_at: new Date().toISOString(),
            },
          ],
        });
      }
      return Promise.resolve({ data: [] }); // Default for other endpoints
    });
    
    render(<App />);
    
    // Wait for tasks to be displayed
    await waitFor(() => {
      expect(screen.getByText('Test task 1')).toBeInTheDocument();
      expect(screen.getByText('Test task 2')).toBeInTheDocument();
    });
  });

  test('displays agents from API', async () => {
    // Mock agents API response
    axios.get.mockImplementation((url) => {
      if (url === '/api/agents') {
        return Promise.resolve({
          data: [
            {
              agent_id: '1',
              name: 'Executor Agent',
              is_active: true,
            },
            {
              agent_id: '2',
              name: 'Browser Agent',
              is_active: false,
            },
          ],
        });
      }
      return Promise.resolve({ data: [] }); // Default for other endpoints
    });
    
    render(<App />);
    
    // Wait for agents to be displayed
    await waitFor(() => {
      expect(screen.getByText('Executor Agent')).toBeInTheDocument();
      expect(screen.getByText('Browser Agent')).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    // Mock API error
    axios.post.mockRejectedValueOnce(new Error('Network error'));
    axios.get.mockResolvedValue({ data: [] }); // Mock empty tasks and agents lists
    
    render(<App />);
    const inputElement = screen.getByPlaceholderText(/Type your message here/i);
    const sendButton = screen.getByText(/Send/i);
    
    // Type and send a message
    fireEvent.change(inputElement, { target: { value: 'Hello Ashus AI' } });
    fireEvent.click(sendButton);
    
    // Check that error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Error: Could not send message/i)).toBeInTheDocument();
    });
  });
});
