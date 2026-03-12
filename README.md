# Todo AI Chatbot

An AI-powered chatbot for managing todos through natural language using Model Context Protocol (MCP) architecture. The system exposes task management operations as FastMCP tools that a Gemini agent (via OpenRouter) calls based on user intent parsed from conversational input.

## Features

- **Natural Language Processing**: Create, list, complete, update, and delete tasks using natural language
- **Persistent Conversations**: Chat history saved to Neon PostgreSQL database
- **Multi-tenant**: Strict user data isolation with authentication
- **MCP Architecture**: Separated task operations from AI logic for reusability
- **Web Interface**: React-based frontend for easy interaction

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)      │◄──►│   (Neon PG)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                            │
                    ┌──────────────────┐
                    │   AI Agent       │
                    │  (Gemini/OpenAI) │
                    └──────────────────┘
                            │
                    ┌──────────────────┐
                    │   MCP Tools      │
                    │ (add,list,etc.)  │
                    └──────────────────┘
```

### Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLModel, asyncpg
- **Frontend**: React 18+, Vite, JavaScript/HTML/CSS
- **Database**: PostgreSQL (Neon Serverless)
- **AI**: OpenAI/Gemini via OpenRouter with MCP tools
- **Authentication**: Better Auth (planned)
- **Deployment**: Docker containerized

## API Endpoints

### Chat Endpoint

**POST** `/api/{user_id}/chat`

Send a chat message and get AI response.

#### Request Body
```json
{
  "message": "string (required)",
  "conversation_id": "string (optional, UUID format)"
}
```

#### Response
```json
{
  "response": "string",
  "conversation_id": "string (UUID)",
  "message_id": "string (UUID)"
}
```

#### Examples

Start a new conversation:
```bash
curl -X POST http://localhost:8000/api/test-user-123/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task to buy groceries"}'
```

Continue existing conversation:
```bash
curl -X POST http://localhost:8000/api/test-user-123/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my pending tasks",
    "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
  }'
```

### Health Check

**GET** `/health`

Check if the service is running.

#### Response
```json
{
  "status": "healthy",
  "timestamp": "2026-01-03T10:30:00Z",
  "database": "connected"
}
```

## OpenAPI Documentation

The API includes auto-generated OpenAPI documentation available at:
- `/docs` - Interactive Swagger UI
- `/redoc` - ReDoc documentation

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/dbname

# OpenAI (or OpenRouter)
OPENAI_API_KEY=sk-proj-...  # Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini   # Or your preferred model

# Better Auth (Optional for Phase 1, Required for Phase 5)
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:8000

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Deployment

### Docker Deployment

Build and run with Docker:

```bash
# Build the Docker image
docker build -t todo-chatbot .

# Run with environment variables
docker run --env-file .env -p 8000:8000 todo-chatbot
```

### Daily Usage (Recommended)

**For everyday use, simply double-click the `start_todo.bat` file on your Desktop:**

1. Double-click `start_todo.bat` on your Desktop
2. The script will automatically start both backend and frontend servers
3. Your browser will open automatically to `http://localhost:5174`
4. Both servers will run in separate command windows
5. To stop, press Ctrl+C in both command windows or double-click `stop_todo.bat`

## Development Setup

1. **Prerequisites**
   - Python 3.11+
   - PostgreSQL (local or Neon account)
   - Node.js 18+ (for frontend)
   - Git

2. **Backend Setup**
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd todo-ai-chatbot

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install backend dependencies
   cd backend
   pip install -r requirements.txt

   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration

   # Run database migrations
   alembic upgrade head
   ```

3. **Frontend Setup**
   ```bash
   # Install frontend dependencies
   cd ../frontend
   npm install

   # Start development server
   npm run dev
   ```

4. **Start Backend Server**
   ```bash
   # From backend directory
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Available Scripts

### Backend
- `uvicorn src.main:app --reload` - Start development server
- `alembic upgrade head` - Apply database migrations
- `alembic revision --autogenerate -m "message"` - Generate new migration
- `pytest` - Run tests

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Natural Language Commands

The AI agent understands various natural language commands:

### Task Creation
- "Add task to buy groceries"
- "Create a task to call the doctor"
- "Remember to finish the report"
- "I need to pick up dry cleaning"

### Task Listing
- "Show my tasks"
- "What do I need to do?"
- "Show pending tasks"
- "What's on my todo list?"

### Task Completion
- "Complete buy groceries"
- "Mark call doctor as done"
- "Finish finish the report"
- "I'm done with pick up dry cleaning"

### Task Update
- "Change buy groceries to buy organic groceries"
- "Update call doctor to call dentist"
- "Modify finish the report to finish the proposal"

### Task Deletion
- "Delete buy groceries"
- "Remove call doctor"
- "Cancel finish the report"

## Database Schema

The application uses the following tables:

### Task
- `id`: UUID (Primary Key)
- `user_id`: String (Foreign Key)
- `title`: String (max 200 chars)
- `description`: String (max 2000 chars, optional)
- `completed`: Boolean (default: false)
- `created_at`: DateTime
- `updated_at`: DateTime

### Conversation
- `id`: UUID (Primary Key)
- `user_id`: String (Foreign Key)
- `created_at`: DateTime
- `updated_at`: DateTime

### Message
- `id`: UUID (Primary Key)
- `user_id`: String (Foreign Key)
- `conversation_id`: String (Foreign Key)
- `role`: String ('user' or 'assistant')
- `content`: Text
- `created_at`: DateTime

## Error Handling

The application includes comprehensive error handling:
- User authentication and authorization
- Input validation with clear error messages
- Database transaction management
- Graceful handling of AI service failures
- Structured logging for debugging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Startup Scripts

Two convenient batch scripts are provided for easy daily usage:

- **`start_todo.bat`** - Located on your Desktop
  - Starts both backend (port 8000) and frontend (port 5174) servers
  - Automatically opens your browser to the application
  - Runs each server in a separate command window

- **`stop_todo.bat`** - Located on your Desktop
  - Safely stops both backend and frontend servers
  - Kills processes running on ports 8000 and 5174
  - Cleans up any related processes

## Support

For support, please open an issue in the GitHub repository.