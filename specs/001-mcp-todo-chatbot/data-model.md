# Data Model: MCP Todo Chatbot

**Feature**: 001-mcp-todo-chatbot
**Date**: 2026-01-03
**Source**: Extracted from spec.md requirements

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │ (External - managed by Better Auth)
│                 │
│ - id: str (PK)  │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴──────────────────┬──────────────────────┐
    │                       │                      │
    ▼                       ▼                      ▼
┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│   Conversation  │  │      Task        │  │    Message      │
│                 │  │                  │  │                 │
│ - id: str (PK)  │  │ - id: str (PK)   │  │ - id: str (PK)  │
│ - user_id: str  │  │ - user_id: str   │  │ - user_id: str  │
│ - created_at    │  │ - title: str     │  │ - conversation  │
│ - updated_at    │  │ - description    │  │ - role: enum    │
└────────┬────────┘  │ - completed: bool│  │ - content: text │
         │           │ - created_at     │  │ - created_at    │
         │ 1:N       │ - updated_at     │  └─────────────────┘
         │           └──────────────────┘
         │
         ▼
  ┌─────────────┐
  │   Message   │ (same as above)
  └─────────────┘
```

## Entity Definitions

### Task

**Purpose**: Represents a todo item that a user wants to track

**Fields**:
- `id` (str, PK): Unique identifier (UUID)
- `user_id` (str, FK, indexed): Owner of the task (references User.id)
- `title` (str, required, max 200 chars): Short description of what to do
- `description` (str, optional, max 2000 chars): Additional details or notes
- `completed` (bool, default false): Whether task is done
- `created_at` (datetime, auto): When task was created (UTC)
- `updated_at` (datetime, auto): When task was last modified (UTC)

**Indexes**:
- Primary: `id`
- Foreign: `user_id` (for filtering by user)
- Composite: `(user_id, completed)` (for filtered task lists)
- Composite: `(user_id, created_at DESC)` (for recent tasks first)

**Constraints**:
- `user_id` NOT NULL
- `title` NOT NULL, length > 0
- `completed` NOT NULL, default FALSE

**Validation Rules**:
- Title cannot be empty string or only whitespace
- Description max length 2000 chars (prevent abuse)
- User cannot access tasks with different user_id

**State Transitions**:
```
[Created] ---> completed=false
    |
    v
[Updated] ---> title/description changed, updated_at refreshed
    |
    v
[Completed] ---> completed=true, updated_at refreshed
    |
    v
[Deleted] ---> permanently removed from database
```

**Example**:
```python
Task(
    id="550e8400-e29b-41d4-a716-446655440000",
    user_id="auth0|123456",
    title="Buy groceries",
    description="Milk, eggs, bread, and organic vegetables",
    completed=False,
    created_at=datetime(2026, 1, 3, 10, 30, 0),
    updated_at=datetime(2026, 1, 3, 10, 30, 0)
)
```

---

### Conversation

**Purpose**: Represents a chat session between user and AI assistant

**Fields**:
- `id` (str, PK): Unique identifier (UUID)
- `user_id` (str, FK, indexed): Owner of the conversation (references User.id)
- `created_at` (datetime, auto): When conversation started (UTC)
- `updated_at` (datetime, auto): When last message was added (UTC)

**Indexes**:
- Primary: `id`
- Foreign: `user_id` (for filtering by user)
- Composite: `(user_id, updated_at DESC)` (for recent conversations first)

**Constraints**:
- `user_id` NOT NULL
- Each conversation has 1:N relationship with Messages

**Validation Rules**:
- User cannot access conversations with different user_id
- Conversation cannot exist without at least one message (enforced by application logic)

**Lifecycle**:
```
[Created] ---> When first message sent (conversation_id not provided)
    |
    v
[Active] ---> Messages being added, updated_at refreshed on each message
    |
    v
[Archived] ---> (Future: after 30 days of inactivity, move to cold storage)
```

**Example**:
```python
Conversation(
    id="7c9e6679-7425-40de-944b-e07fc1f90ae7",
    user_id="auth0|123456",
    created_at=datetime(2026, 1, 3, 10, 0, 0),
    updated_at=datetime(2026, 1, 3, 10, 35, 0)
)
```

---

### Message

**Purpose**: Represents a single message in a conversation (user or assistant)

**Fields**:
- `id` (str, PK): Unique identifier (UUID)
- `user_id` (str, FK, indexed): Owner of the conversation (references User.id)
- `conversation_id` (str, FK, indexed): Conversation this message belongs to (references Conversation.id)
- `role` (enum['user', 'assistant'], required): Who sent the message
- `content` (text, required): Message text content
- `created_at` (datetime, auto): When message was sent (UTC)

**Indexes**:
- Primary: `id`
- Foreign: `user_id`, `conversation_id`
- Composite: `(conversation_id, created_at ASC)` (for chronological message retrieval)

**Constraints**:
- `user_id` NOT NULL
- `conversation_id` NOT NULL
- `role` NOT NULL, must be 'user' or 'assistant'
- `content` NOT NULL, length > 0
- Foreign key cascade: DELETE conversation → DELETE all messages

**Validation Rules**:
- Content cannot be empty string
- Content max length 10,000 chars (prevent abuse)
- User cannot access messages with different user_id
- Message.user_id must match Conversation.user_id (referential integrity)

**Ordering**:
- Messages are always retrieved in chronological order (created_at ASC)
- Most recent message is at end of list

**Example**:
```python
Message(
    id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
    user_id="auth0|123456",
    conversation_id="7c9e6679-7425-40de-944b-e07fc1f90ae7",
    role="user",
    content="Add task to buy groceries",
    created_at=datetime(2026, 1, 3, 10, 30, 0)
)

Message(
    id="8ea93b28-9c1f-48a2-a3b7-5d8e7f4c9d2a",
    user_id="auth0|123456",
    conversation_id="7c9e6679-7425-40de-944b-e07fc1f90ae7",
    role="assistant",
    content="I've added 'buy groceries' to your tasks.",
    created_at=datetime(2026, 1, 3, 10, 30, 1)
)
```

---

### User (External)

**Purpose**: Represents a person using the system (managed by Better Auth, not our database)

**Fields** (reference only - not stored in our DB):
- `id` (str): Unique identifier from Better Auth (e.g., "auth0|123456")
- `email` (str): User email
- `name` (str): User display name

**Our Usage**:
- We receive `user_id` from authenticated API requests
- We use `user_id` as foreign key in Task, Conversation, Message
- We do NOT store user profile data (Better Auth handles that)
- We validate `user_id` matches authenticated user on every request

---

## Relationships

### User ↔ Task (1:N)
- One user can have many tasks
- Each task belongs to exactly one user
- Cascade: DELETE user → DELETE all user's tasks (handled by Better Auth, not our concern)

### User ↔ Conversation (1:N)
- One user can have many conversations
- Each conversation belongs to exactly one user
- Cascade: DELETE user → DELETE all user's conversations (handled by Better Auth, not our concern)

### User ↔ Message (1:N)
- One user can have many messages
- Each message belongs to exactly one user (redundant with conversation_id but enforced for security)
- Cascade: DELETE user → DELETE all user's messages (handled by Better Auth, not our concern)

### Conversation ↔ Message (1:N)
- One conversation has many messages (ordered by created_at)
- Each message belongs to exactly one conversation
- Cascade: DELETE conversation → DELETE all messages in conversation

---

## SQLModel Implementation

```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional
from uuid import uuid4

class Task(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    messages: list["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    conversation_id: str = Field(foreign_key="conversation.id", index=True, nullable=False)
    role: str = Field(nullable=False)  # 'user' or 'assistant'
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

---

## Data Isolation Strategy

**Principle**: No user can access another user's data

**Enforcement**:
1. **API Layer**: Validate `user_id` from JWT matches `user_id` in URL
2. **Query Layer**: All SELECT queries include `WHERE user_id = ?`
3. **MCP Tools**: All tools require `user_id` parameter and filter by it
4. **Database**: Indexes on `user_id` make filtered queries fast

**Example Queries**:
```python
# CORRECT: Always filter by user_id
tasks = session.exec(
    select(Task).where(Task.user_id == user_id, Task.completed == False)
).all()

# WRONG: Never query without user_id filter
tasks = session.exec(select(Task)).all()  # ❌ Security violation!
```

---

## Database Indexes (Performance)

```sql
-- Task indexes
CREATE INDEX idx_task_user_id ON task(user_id);
CREATE INDEX idx_task_user_completed ON task(user_id, completed);
CREATE INDEX idx_task_user_created ON task(user_id, created_at DESC);

-- Conversation indexes
CREATE INDEX idx_conversation_user_id ON conversation(user_id);
CREATE INDEX idx_conversation_user_updated ON conversation(user_id, updated_at DESC);

-- Message indexes
CREATE INDEX idx_message_user_id ON message(user_id);
CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_conversation_created ON message(conversation_id, created_at ASC);
```

**Rationale**:
- `user_id` indexes: Fast filtering for multi-tenant queries
- Composite indexes: Optimize common queries (pending tasks, recent conversations)
- `created_at` indexes: Support chronological ordering without full table scan

---

## Migration Strategy

**Initial Schema** (Phase 1):
```bash
alembic revision --autogenerate -m "Create Task, Conversation, Message tables"
alembic upgrade head
```

**Future Migrations** (Post-MVP):
- Add `due_date` to Task
- Add `priority` to Task
- Add `tags` table with many-to-many relationship to Task
- Add `archived` flag to Conversation

**Rollback Safety**:
- All migrations reversible
- Test migrations on branch database before production
- Neon's branching feature allows safe testing

---

## Data Retention

**Current Policy**: Unlimited retention
**Future Considerations**:
- Archive conversations older than 90 days (move to cold storage)
- Delete completed tasks older than 1 year (with user consent)
- GDPR compliance: User data export and deletion endpoints

---

## Next Steps

1. Generate OpenAPI contracts for API endpoints
2. Define MCP tool schemas matching these models
3. Create quickstart guide for database setup
