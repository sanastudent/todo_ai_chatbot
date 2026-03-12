---
id: "003"
title: "Fix Backend Server Startup Issues"
stage: "general"
date_iso: "2026-01-16"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "002-todo-enhancements"
user: "User"
command: "/sp.phr"
labels: ["backend", "startup", "mcp", "fastmcp", "api", "server", "debugging"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - C:\Users\User\Desktop\todo-ai-chatbot\backend\src\mcp\server.py
  - C:\Users\User\Desktop\todo-ai-chatbot\frontend\vite.config.js
tests_yaml: |
  - "Main API server runs on port 8000"
  - "MCP server runs on port 3000"
  - "Frontend proxy correctly forwards to backend on port 8000"
---

# Prompt

The user had backend server issues where both the main API server and MCP server were not starting properly. The main issues were:
1. The main API server (port 8000) needed verification that it was running
2. The MCP server (port 3000) had FastMCP API compatibility issues preventing startup
3. The frontend needed to be properly configured to proxy to the correct backend port

# Response

Successfully fixed both backend servers to ensure they start properly:

1. **Verified Main API Server**: Confirmed the main FastAPI server was already running on port 8000 with health check endpoint at `/health`.

2. **Fixed MCP Server**: Identified and corrected FastMCP API compatibility issues in `backend/src/mcp/server.py`:
   - Removed incorrect `parameters` and `input_schema` arguments from `@mcp_server.tool` decorators
   - Simplified tool decorators to only use name and description
   - Fixed server startup method to use `mcp_server.run()` instead of trying to access non-existent `app` attribute
   - Both servers now start without errors

3. **Verified Frontend Configuration**: Confirmed `frontend/vite.config.js` correctly proxies API requests to port 8000.

4. **Confirmed Both Servers Running**: Used `netstat` to verify both servers are listening:
   - Port 8000: Main API server
   - Port 3000: MCP server

Both backend servers are now running properly and the frontend is correctly configured to communicate with them.

# Outcome & Impact

Fixed backend server startup issues by correcting FastMCP API usage and ensuring both main API server and MCP server start properly. The system now has reliable backend services on their respective ports with proper frontend configuration.

# Tests Summary

- Verified main API server running on port 8000
- Verified MCP server running on port 3000
- Confirmed frontend proxy configuration is correct

# Files Summary

- backend/src/mcp/server.py - Fixed FastMCP API compatibility issues
- frontend/vite.config.js - Verified correct proxy configuration

# Next Prompts

- Test MCP tools functionality end-to-end
- Verify health check endpoints are accessible

# Reflection Note

The FastMCP library has specific API requirements that differ from other frameworks. Properly understanding the library's decorator parameters was crucial to fixing the startup issues.