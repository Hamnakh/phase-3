# Data Model: Full-Stack Todo App with Authentication

**Feature**: 001-fullstack-todo-auth
**Date**: 2025-12-27

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│               User                  │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ email: String (unique, not null)    │
│ name: String (nullable)             │
│ created_at: DateTime                │
│ updated_at: DateTime                │
└─────────────────────────────────────┘
                │
                │ 1:N
                ▼
┌─────────────────────────────────────┐
│               Todo                  │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ title: String (not null, max 500)   │
│ completed: Boolean (default false)  │
│ user_id: UUID (FK → User.id)        │
│ created_at: DateTime                │
│ updated_at: DateTime                │
└─────────────────────────────────────┘
```

## Entities

### User

Represents a registered account holder in the system. Managed by Better Auth on the frontend.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Unique identifier (from Better Auth) |
| email | String | Unique, Not Null, Max 255 | User's email address |
| name | String | Nullable, Max 100 | Display name (optional) |
| created_at | DateTime | Not Null, Default NOW | Account creation timestamp |
| updated_at | DateTime | Not Null, Auto-update | Last modification timestamp |

**Notes**:
- Password is NOT stored in backend - Better Auth handles authentication
- `id` matches the `sub` claim in JWT tokens
- Backend only needs minimal user info for data isolation

### Todo

Represents a task item belonging to a single user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Unique identifier |
| title | String | Not Null, Max 500 | Task description |
| completed | Boolean | Not Null, Default false | Completion status |
| user_id | UUID | Foreign Key (User.id), Not Null | Owner reference |
| created_at | DateTime | Not Null, Default NOW | Creation timestamp |
| updated_at | DateTime | Not Null, Auto-update | Last modification timestamp |

**Indexes**:
- `idx_todo_user_id` on `user_id` for efficient filtering
- `idx_todo_user_created` on `(user_id, created_at DESC)` for sorted listing

## Relationships

### User → Todo (One-to-Many)

- One User can have zero or more Todos
- Each Todo belongs to exactly one User
- Cascade delete: When User is deleted, all their Todos are deleted
- User isolation: All Todo queries MUST filter by `user_id`

## Validation Rules

### User
- `email`: Valid email format, unique across all users
- `name`: If provided, must be 1-100 characters

### Todo
- `title`: Required, 1-500 characters, trimmed whitespace
- `completed`: Boolean only (true/false)
- `user_id`: Must reference existing user (enforced by FK)

## State Transitions

### Todo Lifecycle

```
┌─────────┐     create      ┌─────────────┐
│  (none) │ ───────────────▶│  Incomplete │
└─────────┘                 └─────────────┘
                                  │ │
                      toggle      │ │     toggle
                      complete    │ │     incomplete
                                  ▼ │
                            ┌─────────────┐
                            │  Completed  │
                            └─────────────┘
                                  │
                      delete      │
                                  ▼
                            ┌─────────────┐
                            │  (deleted)  │
                            └─────────────┘
```

**Valid Transitions**:
- Create: → Incomplete
- Toggle Complete: Incomplete ↔ Completed
- Update Title: Any state (stays in same state)
- Delete: Any state → Deleted

## SQLModel Definitions

### User Model (Backend)

```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    name: str | None = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Todo Model (Backend)

```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=500)
    completed: bool = Field(default=False)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## TypeScript Interfaces (Frontend)

```typescript
interface User {
  id: string;
  email: string;
  name?: string;
  createdAt: string;
  updatedAt: string;
}

interface Todo {
  id: string;
  title: string;
  completed: boolean;
  userId: string;
  createdAt: string;
  updatedAt: string;
}

interface CreateTodoRequest {
  title: string;
}

interface UpdateTodoRequest {
  title?: string;
  completed?: boolean;
}
```

## Database Schema (PostgreSQL)

```sql
-- Users table (minimal - Better Auth manages auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Todos table
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_user_created ON todos(user_id, created_at DESC);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_todos_updated_at
    BEFORE UPDATE ON todos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```
