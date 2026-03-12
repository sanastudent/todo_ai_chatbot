import React, { useState, useEffect } from 'react';
import { useBackendHealth, apiService } from './services/apiService';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [userId, setUserId] = useState('');
  const [theme, setTheme] = useState('light');
  const { isHealthy, loading: healthLoading } = useBackendHealth();
  const [backendUnavailable, setBackendUnavailable] = useState(false);

  // Monitor backend health
  useEffect(() => {
    console.log('[APP] Health check effect triggered');
    console.log('[APP] isHealthy:', isHealthy);
    console.log('[APP] backendUnavailable (before):', backendUnavailable);

    if (isHealthy !== null) {
      const wasUnavailable = backendUnavailable;
      const newBackendUnavailable = !isHealthy;
      setBackendUnavailable(newBackendUnavailable);

      console.log('[APP] backendUnavailable (after):', newBackendUnavailable);

      if (isHealthy && wasUnavailable) {
        // Backend became available again, show reconnection message
        const reconnectMessage = {
          id: `reconnect-${Date.now()}`,
          content: '✅ Backend reconnected! Previous error messages may be outdated. Feel free to clear the chat if needed.',
          role: 'assistant'
        };
        setMessages(prev => [...prev, reconnectMessage]);
      }
    }
  }, [isHealthy, backendUnavailable]);

  // Initialize theme from localStorage or system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');

    setTheme(initialTheme);
    document.documentElement.setAttribute('data-theme', initialTheme);
  }, []);

  // Toggle theme function
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  // Check if user is logged in on component mount
  useEffect(() => {
    const storedUsername = localStorage.getItem('username');
    const storedUserId = localStorage.getItem('userId');

    if (storedUsername && storedUserId) {
      setIsLoggedIn(true);
      setUsername(storedUsername);
      setUserId(storedUserId);
    }
  }, []);

  // Add initial welcome message when logged in
  useEffect(() => {
    if (isLoggedIn) {
      setMessages([
        {
          id: 'welcome',
          content: `Welcome back, ${username}! I'm your AI assistant. You can ask me to add tasks, list tasks, complete tasks, and more. Try saying 'Add task to buy groceries'!`,
          role: 'assistant'
        }
      ]);
    }
  }, [isLoggedIn, username]);

  const handleLogin = (e) => {
    e.preventDefault();
    if (username.trim()) {
      // Generate a unique user ID if not already set
      const storedUserId = localStorage.getItem('userId');
      const newUserId = storedUserId || 'user-' + Date.now();

      localStorage.setItem('username', username);
      localStorage.setItem('userId', newUserId);

      setUserId(newUserId);
      setIsLoggedIn(true);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('username');
    localStorage.removeItem('userId');
    setIsLoggedIn(false);
    setUsername('');
    setUserId('');
    setMessages([]);
  };

  const handleClearChat = () => {
    // Clear all messages and show welcome message
    setMessages([
      {
        id: 'welcome',
        content: `Welcome back, ${username}! I'm your AI assistant. You can ask me to add tasks, list tasks, complete tasks, and more. Try saying 'Add task to buy groceries'!`,
        role: 'assistant'
      }
    ]);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    console.log('[APP] handleSendMessage called');
    console.log('[APP] inputValue:', inputValue);
    console.log('[APP] isLoggedIn:', isLoggedIn);
    console.log('[APP] userId:', userId);

    if (!inputValue.trim() || !isLoggedIn) {
      console.log('[APP] Early return - empty input or not logged in');
      return;
    }

    // Add user message to UI immediately
    const userMessage = {
      id: Date.now().toString(),
      content: inputValue,
      role: 'user'
    };
    setMessages(prev => [...prev, userMessage]);
    const userInput = inputValue;
    setInputValue('');

    console.log('[APP] About to call apiService.request');
    console.log('[APP] Endpoint:', `/${userId}/chat`);
    console.log('[APP] Message:', userInput);

    try {
      // Use apiService to make the request
      const data = await apiService.request(`/${userId}/chat`, {
        method: 'POST',
        body: JSON.stringify({
          message: userInput
        })
      });

      console.log('[APP] Received response:', data);

      const assistantMessage = {
        id: data.message_id || `assistant-${Date.now()}`,
        content: data.response,
        role: 'assistant'
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('[APP] Error caught:', error);
      console.error('[APP] Error message:', error.message);

      // Check if this is a network error
      if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        setBackendUnavailable(true);

        const errorMessage = {
          id: `error-${Date.now()}`,
          content: `Connection failed: ${error.message}. Backend may be down.`,
          role: 'assistant'
        };
        setMessages(prev => [...prev, errorMessage]);
      } else {
        const errorMessage = {
          id: `error-${Date.now()}`,
          content: `Error: ${error.message}`,
          role: 'assistant'
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="app-container">
        {backendUnavailable && (
          <div className="alert alert-warning card p-md mb-md" style={{
            backgroundColor: '#fef3c7',
            border: '1px solid #fbbf24',
            color: '#92400e',
            borderRadius: 'var(--radius-md)'
          }}>
            ⚠️ <strong>Backend Unavailable:</strong> The backend server is not responding. Please ensure the backend is running before continuing.
          </div>
        )}
        <div className="card" style={{ maxWidth: '400px', width: '100%', padding: 'var(--spacing-lg)', backgroundColor: '#dcfce7' }}>
          <h2 className="text-center">Todo AI Dashboard</h2>
          <p className="text-center mb-lg" style={{ color: 'var(--text-secondary)' }}>Sign in to manage your tasks with AI assistance</p>

          <form onSubmit={handleLogin} className="flex flex-col gap-md">
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your name"
              className="p-md"
              style={{
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                backgroundColor: 'var(--bg-secondary)'
              }}
              required
            />

            <button
              type="submit"
              className="btn btn-primary p-md"
              style={{
                backgroundColor: 'var(--btn-primary-bg)',
                color: 'var(--btn-primary-text)',
                border: 'none'
              }}
            >
              Sign In
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="dashboard" style={{ maxWidth: '1000px', width: '100%' }}>
        {/* Backend Unavailable Warning */}
        {backendUnavailable && (
          <div className="alert alert-warning card p-md mb-md" style={{
            backgroundColor: '#fef3c7',
            border: '1px solid #fbbf24',
            color: '#92400e',
            borderRadius: 'var(--radius-md)'
          }}>
            ⚠️ <strong>Backend Unavailable:</strong> The backend server is not responding. Please ensure the backend is running.
          </div>
        )}

        {/* Header */}
        <header className="card p-md mb-md" style={{
          background: `linear-gradient(135deg, var(--header-gradient-start), var(--header-gradient-end))`,
          color: 'white',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--card-shadow)'
        }}>
          <div className="flex justify-between items-center">
            <div>
              <h1 style={{ color: 'white' }}>Todo AI Dashboard</h1>
              <p style={{ color: 'rgba(255, 255, 255, 0.9)' }}>Welcome back, {username}!</p>
            </div>
            <div className="flex gap-md">
              <button
                onClick={toggleTheme}
                className="btn btn-secondary"
                style={{
                  minWidth: 'auto',
                  padding: '0.5rem',
                  backgroundColor: 'var(--btn-secondary-bg)',
                  color: 'var(--btn-secondary-text)',
                  border: '1px solid var(--border-color)'
                }}
              >
                {theme === 'light' ? '🌙' : '☀️'}
              </button>
              <button
                onClick={handleLogout}
                className="btn"
                style={{
                  backgroundColor: 'var(--btn-secondary-bg)',
                  color: 'var(--btn-secondary-text)',
                  border: '1px solid var(--border-color)'
                }}
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-2 gap-lg mb-lg" style={{ backgroundColor: '#dcfce7', padding: 'var(--spacing-md)', borderRadius: 'var(--radius-lg)' }}>
          {/* Quick Stats */}
          <div className="card p-lg" style={{ backgroundColor: '#dbeafe' }}>
            <h3 className="mb-md">Quick Stats</h3>
            <div className="flex gap-md">
              <div className="flex-1 text-center p-md" style={{
                background: 'linear-gradient(135deg, var(--stats-gradient-start), var(--stats-gradient-end))',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-color)',
                color: 'white'
              }}>
                <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'bold', color: 'white' }}>0</div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'rgba(255, 255, 255, 0.9)' }}>Total Tasks</div>
              </div>
              <div className="flex-1 text-center p-md" style={{
                background: 'linear-gradient(135deg, var(--stats-gradient-start), var(--stats-gradient-end))',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-color)',
                color: 'white'
              }}>
                <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'bold', color: 'white' }}>0</div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'rgba(255, 255, 255, 0.9)' }}>Completed</div>
              </div>
              <div className="flex-1 text-center p-md" style={{
                background: 'linear-gradient(135deg, var(--stats-gradient-start), var(--stats-gradient-end))',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-color)',
                color: 'white'
              }}>
                <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 'bold', color: 'white' }}>0</div>
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'rgba(255, 255, 255, 0.9)' }}>Pending</div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card p-lg" style={{ backgroundColor: '#dbeafe' }}>
            <h3 className="mb-md">Quick Actions</h3>
            <div className="flex gap-sm flex-wrap">
              <button
                onClick={() => setInputValue('Add task')}
                className="btn"
                style={{
                  padding: '0.5rem 1rem',
                  fontSize: 'var(--font-size-sm)',
                  backgroundColor: 'var(--btn-primary-bg)',
                  color: 'var(--btn-primary-text)',
                  border: 'none'
                }}
                disabled={backendUnavailable}
              >
                Add Task
              </button>
              <button
                onClick={() => setInputValue('Show my tasks')}
                className="btn"
                style={{
                  padding: '0.5rem 1rem',
                  fontSize: 'var(--font-size-sm)',
                  backgroundColor: 'var(--btn-primary-bg)',
                  color: 'var(--btn-primary-text)',
                  border: 'none'
                }}
                disabled={backendUnavailable}
              >
                Show Tasks
              </button>
              <button
                onClick={() => setInputValue('Complete task 1')}
                className="btn"
                style={{
                  padding: '0.5rem 1rem',
                  fontSize: 'var(--font-size-sm)',
                  backgroundColor: 'var(--btn-primary-bg)',
                  color: 'var(--btn-primary-text)',
                  border: 'none'
                }}
                disabled={backendUnavailable}
              >
                Complete Task
              </button>
              <button
                onClick={() => setInputValue('Help')}
                className="btn"
                style={{
                  padding: '0.5rem 1rem',
                  fontSize: 'var(--font-size-sm)',
                  backgroundColor: 'var(--btn-primary-bg)',
                  color: 'var(--btn-primary-text)',
                  border: 'none'
                }}
                disabled={backendUnavailable}
              >
                Help
              </button>
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div className="card" style={{ height: '500px', display: 'flex', flexDirection: 'column', backgroundColor: '#dcfce7' }}>
          <div className="p-md" style={{
            borderBottom: '1px solid var(--border-color)',
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-lg) var(--radius-lg) 0 0',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <h2>AI Assistant</h2>
              <p>Ask me anything about your tasks</p>
            </div>
            <button
              onClick={handleClearChat}
              className="btn"
              style={{
                padding: '0.5rem 1rem',
                fontSize: 'var(--font-size-sm)',
                backgroundColor: 'var(--btn-secondary-bg)',
                color: 'var(--btn-secondary-text)',
                border: '1px solid var(--border-color)',
                minWidth: 'auto'
              }}
              title="Clear chat history"
            >
              🗑️ Clear Chat
            </button>
          </div>

          <div className="chat-messages flex-1 overflow-y-auto p-lg flex flex-col gap-md" style={{ backgroundColor: 'var(--bg-primary)' }}>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.role}`}
                style={{
                  alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '80%',
                  padding: 'var(--spacing-md) var(--spacing-lg)',
                  borderRadius: 'var(--radius-lg)',
                  backgroundColor: message.role === 'user' ? 'var(--chat-user-bg)' : 'var(--chat-assistant-bg)',
                  color: 'var(--text-primary)',
                  wordWrap: 'break-word',
                  boxShadow: 'var(--card-shadow)',
                  border: '1px solid var(--border-color)'
                }}
              >
                {message.content}
              </div>
            ))}
          </div>

          <form onSubmit={handleSendMessage} className="p-md" style={{
            borderTop: '1px solid var(--border-color)',
            backgroundColor: 'var(--bg-primary)',
            borderRadius: '0 0 var(--radius-lg) var(--radius-lg)',
            display: 'flex',
            gap: 'var(--spacing-md)'
          }}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={backendUnavailable ? "Backend unavailable - please start the backend server" : "Type your message..."}
              className="flex-1 p-md"
              style={{
                borderRadius: 'var(--radius-lg)',
                border: '1px solid #3b82f6',
                backgroundColor: backendUnavailable ? '#f9fafb' : '#ffffff',
                color: 'var(--text-primary)'
              }}
              disabled={backendUnavailable}
              onClick={() => {
                console.log('[APP] Input clicked');
                console.log('[APP] backendUnavailable:', backendUnavailable);
                console.log('[APP] isHealthy:', isHealthy);
              }}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || backendUnavailable}
              className="btn btn-primary p-md"
              onClick={(e) => {
                console.log('[APP] Send button clicked');
                console.log('[APP] inputValue:', inputValue);
                console.log('[APP] inputValue.trim():', inputValue.trim());
                console.log('[APP] backendUnavailable:', backendUnavailable);
                console.log('[APP] Button disabled:', !inputValue.trim() || backendUnavailable);
              }}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;