"""
Index file for the Ashus AI frontend application.
This file serves as the entry point for the React application.
"""

import React from 'react';
import ReactDOM from 'react-dom';
import App from './components/App';
import './styles/App.css';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
