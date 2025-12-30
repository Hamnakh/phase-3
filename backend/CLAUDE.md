# Backend Development Guidelines

Auto-generated from feature plans. Last updated: 2025-12-27

## Active Technologies

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT verification (tokens issued by Better Auth)

## Project Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User SQLModel
│   │   └── todo.py          # Todo SQLModel
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth endpoints
│   │   └── todos.py         # Todo CRUD endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth.py          # JWT verification
│   └── schemas/
│       ├── __init__.py
│       ├── todo.py          # Pydantic schemas
│       └── user.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_todos.py
├── requirements.txt
├── .env
└── .env.example
```

## Commands

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

## Code Style

### Python
- Follow PEP 8
- Use type hints everywhere
- Use `async/await` for database operations

### FastAPI
- Use dependency injection for auth
- Use Pydantic models for request/response
- Document endpoints with docstrings

### SQLModel
- Define models with proper relationships
- Use UUID for primary keys
- Include `created_at` and `updated_at` timestamps

## Environment Variables

Required in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require
JWT_SECRET=<shared-secret-with-frontend>
CORS_ORIGINS=http://localhost:3000
```

## Key Patterns

### JWT Verification Dependency

```python
# app/services/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
```

### User Data Isolation

```python
# app/routers/todos.py
@router.get("/todos")
async def list_todos(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # ALWAYS filter by user_id - Constitution V requirement
    result = await db.execute(
        select(Todo).where(Todo.user_id == user_id)
    )
    return result.scalars().all()
```

### Error Handling

```python
# Return proper HTTP status codes
@router.get("/todos/{todo_id}")
async def get_todo(
    todo_id: UUID,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    todo = await db.get(Todo, todo_id)
    if not todo or todo.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo
```

## Security Requirements

Per Constitution V:

1. **All endpoints MUST verify JWT** - Use `get_current_user` dependency
2. **All queries MUST filter by user_id** - Never return other users' data
3. **401 for invalid/missing token** - Consistent error response
4. **404 for not found OR not owned** - No information leakage

## Recent Changes

- 001-fullstack-todo-auth: Initial FastAPI setup, JWT verification, Todo CRUD

<!-- MANUAL ADDITIONS START -->
<!-- Add any manual overrides or notes below this line -->
<!-- MANUAL ADDITIONS END -->
