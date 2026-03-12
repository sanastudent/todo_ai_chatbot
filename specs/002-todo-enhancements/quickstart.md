# Quickstart Guide: Todo AI Chatbot Enhanced Features

## Overview
This guide provides instructions for setting up and using the enhanced Todo AI Chatbot with priority levels, tagging system, search functionality, filtering capabilities, and sorting options.

## Prerequisites
- Python 3.11+
- Node.js 16+ (for frontend development)
- PostgreSQL-compatible database (Neon recommended)
- Access to OpenRouter API for AI capabilities
- Git for version control

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd todo-ai-chatbot
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database URL, OpenRouter API key, etc.
```

### 3. Database Setup
```bash
# Run database migrations (includes the enhanced schema)
alembic upgrade head

# Or initialize the database if starting fresh
python src/init_db.py
```

### 4. Frontend Setup (if applicable)
```bash
cd ../frontend
npm install
cp .env.example .env.local
# Configure frontend environment variables
```

## Enhanced Features Usage

### Priority Levels
Set priority when creating tasks:
- `Add high priority task to call client`
- `Create a task with low priority to organize files`
- `Add medium priority task to review documents`

Update task priority:
- `Change priority of task "call client" to high`
- `Update task "organize files" to low priority`

### Tagging System
Add tags when creating tasks:
- `Add task to prepare presentation with tags work and urgent`
- `Create grocery shopping task with tags personal and weekly`
- `Add workout task tagged with fitness and daily`

Manage tags:
- `Add tag personal to task "grocery shopping"`
- `Remove tag weekly from task "team meeting"`

### Search Functionality
Search across all your tasks:
- `Find tasks about meeting`
- `Search for "presentation" in my tasks`
- `Look for tasks containing "urgent"`

### Filtering Capabilities
Filter tasks by various criteria:
- `Show only high priority tasks`
- `Display tasks with tag work`
- `Show completed tasks`
- `Show pending tasks`
- `Show tasks with tags work or urgent`

### Sorting Options
Sort tasks in different orders:
- `Sort tasks by priority` (high to low)
- `Sort tasks alphabetically`
- `Sort tasks by creation date`
- `Order tasks by priority and then alphabetically`

### Combined Operations
Use multiple features together:
- `Show high priority work tasks sorted by priority`
- `Find urgent tasks and sort them alphabetically`
- `Show incomplete personal tasks tagged with weekly`

## API Integration

### Using Enhanced MCP Tools
The enhanced features are accessible through the MCP tools:

1. **add_task**: Extended with `priority` and `tags` parameters
2. **list_tasks**: Enhanced with filtering, searching, and sorting parameters
3. **update_task**: Extended with `priority` and `tags` update capability

### Example API Calls
```javascript
// Add task with priority and tags
const response = await add_task({
  user_id: "user123",
  title: "Prepare quarterly report",
  priority: "high",
  tags: ["work", "report", "urgent"]
});

// List tasks with filters and sorting
const tasks = await list_tasks({
  user_id: "user123",
  priority: ["high", "medium"],
  tags: ["work"],
  search_term: "report",
  sort_by: "priority",
  sort_order: "desc"
});
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL="postgresql://..."
OPENROUTER_API_KEY="sk-..."
SECRET_KEY="your-secret-key"
DEBUG=true
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
NEXT_PUBLIC_MCP_SERVER_URL="ws://localhost:8000/mcp"
```

## Running the Application

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `DATABASE_URL` in your environment variables
   - Ensure your PostgreSQL/Neon database is accessible
   - Run migrations: `alembic upgrade head`

2. **AI Service Unavailable**
   - Check your OpenRouter API key
   - Verify internet connectivity
   - Confirm the AI service is responding

3. **MCP Tools Not Working**
   - Ensure the MCP server is running
   - Check that all required tools are registered
   - Verify the tool contracts match the specification

### Performance Tips

1. **Large Task Lists**
   - Use filters to narrow down results
   - Implement pagination for large result sets
   - Utilize search terms to find specific tasks quickly

2. **Search Optimization**
   - Use specific keywords for better results
   - Combine search with filters for precision
   - Consider using tags for categorical searches

## Next Steps

1. **Customization**: Adjust the priority values or tag limitations based on your needs
2. **Advanced Queries**: Implement more complex search and filter combinations
3. **Analytics**: Track usage patterns of different features
4. **Integration**: Connect with calendar applications or other productivity tools

## Support

For issues with the enhanced features:
- Check the [documentation](../README.md)
- Review the [API contracts](./contracts/api-contract.yaml)
- Examine the [data model](./data-model.md) for field definitions
- Consult the [implementation plan](./plan.md) for architecture details