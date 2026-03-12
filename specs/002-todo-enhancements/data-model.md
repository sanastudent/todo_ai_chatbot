# Data Model: Todo AI Chatbot Enhanced Task Management

## Overview
This document defines the updated data model for the Todo AI Chatbot with enhanced features including priority levels, tagging system, and improved search/filter capabilities.

## Entity Definitions

### Task (Enhanced)
Represents a todo item that a user wants to track, with additional fields for priority, tags, and improved search capabilities.

#### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | str (UUID) | Primary Key, Required | Unique identifier for the task |
| user_id | str | Index, Required, Foreign Key | User who owns this task |
| title | str | Max 200 chars, Required | Short description of the task |
| description | str \| null | Max 2000 chars, Optional | Additional details about the task |
| completed | bool | Required, Default: false | Whether the task is completed |
| priority | str (ENUM) | Required, Default: "medium", Values: ["high", "medium", "low"] | Priority level of the task |
| tags | JSON array | Optional, Default: [] | Array of tag strings for categorization |
| created_at | datetime | Required, Auto-generated | Timestamp when task was created |
| updated_at | datetime | Required, Auto-generated | Timestamp when task was last updated |

#### Relationships
- **Belongs to**: User (via user_id foreign key)
- **Related to**: Messages (through conversation_id via Conversation)

#### Validation Rules
1. **Priority**: Must be one of "high", "medium", or "low"
2. **Tags**: Must be an array of strings, maximum 10 tags per task
3. **Title uniqueness**: No duplicate titles per user (existing constraint maintained)
4. **Required fields**: All required fields must be present
5. **Character limits**: All character limits enforced as specified

#### State Transitions
- **Created**: When task is first added (completed=false, priority=medium, tags=[])
- **Updated**: When any field is modified (updates updated_at timestamp)
- **Completed**: When task status changes to completed (completed=true, updates updated_at)
- **Deleted**: When task is permanently removed (via delete_task MCP tool)

### Priority Enum
Enumeration defining the priority levels for tasks.

#### Values
- **high**: Critical tasks that require immediate attention
- **medium**: Standard priority tasks (default level)
- **low**: Tasks that can be deferred or are less urgent

### Tag System
Structured approach to categorizing tasks using tags.

#### Tag Constraints
- Each tag must be a string between 1 and 50 characters
- Maximum of 10 tags per task
- Tags are case-insensitive and trimmed of leading/trailing whitespace
- Duplicate tags within a task are prevented
- Tags support alphanumeric characters, hyphens, and underscores only

#### Tag Operations
- **Add**: Append a new tag to the task's tag array
- **Remove**: Remove a specific tag from the task's tag array
- **Replace**: Set the entire tag array to new values
- **Search**: Find tasks containing specific tags

## Database Schema

### Tasks Table (Enhanced)
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',
    tags JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, title),
    FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT valid_priority CHECK (priority IN ('high', 'medium', 'low'))
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_tags ON tasks USING GIN (tags);
CREATE INDEX idx_tasks_priority_completed ON tasks(priority, completed);
```

### Index Strategy
1. **idx_tasks_user_id**: For user-specific queries (existing)
2. **idx_tasks_priority**: For priority-based filtering
3. **idx_tasks_completed**: For completion status filtering
4. **idx_tasks_created_at**: For chronological sorting (existing)
5. **idx_tasks_tags**: For tag-based searching using GIN index
6. **idx_tasks_priority_completed**: For combined priority and status filtering

## Search Implementation

### Full-Text Search Configuration
Tasks support full-text search across title and description fields using PostgreSQL's built-in capabilities.

#### Searchable Fields
- **title**: Primary search target
- **description**: Secondary search target
- **tags**: Tertiary search target (tag content)

#### Search Algorithm
1. **Exact Match**: Check for exact phrase matches first
2. **Partial Match**: Look for partial matches in title/description
3. **Tag Match**: Check for tasks containing matching tags
4. **Ranking**: Rank results by relevance (title > description > tags)

## API Representation

### Task Object (JSON)
```json
{
  "task_id": "uuid-string",
  "user_id": "user-identifier",
  "title": "Task title",
  "description": "Optional description",
  "completed": false,
  "priority": "high",
  "tags": ["work", "urgent"],
  "created_at": "2026-01-14T10:30:00Z",
  "updated_at": "2026-01-14T10:30:00Z"
}
```

### Request Objects
#### Add Task Request
```json
{
  "user_id": "user-identifier",
  "title": "Task title",
  "description": "Optional description",
  "priority": "medium",
  "tags": ["tag1", "tag2"]
}
```

#### Filter Request
```json
{
  "user_id": "user-identifier",
  "priority": ["high", "medium"],
  "tags": ["work"],
  "completed": false,
  "search_term": "keyword",
  "sort_by": "priority",
  "sort_order": "desc"
}
```

## Data Integrity

### Constraints
1. **Referential Integrity**: All foreign keys enforced
2. **Priority Validation**: Only valid priority values allowed
3. **Tag Format**: Tags must match alphanumeric + special characters pattern
4. **User Isolation**: Users can only access their own tasks

### Migration Strategy
1. **Schema Update**: Add new columns with appropriate defaults
2. **Data Migration**: Update existing records with default values
3. **Index Creation**: Add performance indexes after data migration
4. **Validation Setup**: Enable constraints after data cleanup

## Performance Considerations

### Query Optimization
- Use indexes for all common filter operations
- Limit result sets with pagination for large datasets
- Optimize full-text search with proper configuration
- Cache frequently accessed data where appropriate

### Scaling Factors
- Estimated max 1000 tasks per user
- Concurrent users: up to 10,000 (projected)
- Query response time target: <200ms for search/filter operations