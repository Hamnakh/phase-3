# Research: Full-Stack Todo App with Authentication

**Feature**: 001-fullstack-todo-auth
**Date**: 2025-12-27

## Technology Decisions

### 1. Frontend Framework: Next.js 14 (App Router)

**Decision**: Use Next.js 14 with App Router for the frontend.

**Rationale**:
- Constitution mandates Next.js with App Router
- App Router provides server components for improved performance
- Built-in routing reduces boilerplate
- Excellent TypeScript support

**Alternatives Considered**:
- Pages Router: Older pattern, less optimal for new projects
- React + Vite: Would require additional routing setup

### 2. Authentication: Better Auth

**Decision**: Use Better Auth for frontend authentication, issuing JWTs.

**Rationale**:
- Constitution mandates Better Auth
- Handles user registration, login, logout flows
- Issues JWT tokens for API authentication
- Session management built-in

**Implementation Notes**:
- Configure Better Auth with email/password provider
- JWT tokens stored in HTTP-only cookies for security
- Token refresh handled automatically
- Shared secret with backend for JWT verification

### 3. Backend Framework: FastAPI

**Decision**: Use FastAPI with Python 3.11.

**Rationale**:
- Constitution mandates FastAPI
- Automatic OpenAPI documentation
- Async support for better performance
- Excellent Pydantic integration for validation

**Key Dependencies**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `python-jose[cryptography]` - JWT verification
- `passlib[bcrypt]` - Password hashing (if needed for backup)

### 4. ORM: SQLModel

**Decision**: Use SQLModel for database models.

**Rationale**:
- Constitution mandates SQLModel
- Combines SQLAlchemy and Pydantic
- Single model definition for DB and API schemas
- Type-safe database operations

**Implementation Notes**:
- Define User and Todo models with relationships
- Use `user_id` foreign key for data isolation
- Async session support for FastAPI

### 5. Database: Neon Serverless PostgreSQL

**Decision**: Use Neon Serverless PostgreSQL.

**Rationale**:
- Constitution mandates Neon Serverless PostgreSQL
- Serverless scales automatically
- PostgreSQL compatibility
- Connection pooling built-in

**Connection Strategy**:
- Use `asyncpg` driver for async operations
- Connection string via `DATABASE_URL` environment variable
- SSL required for production

### 6. JWT Verification Strategy

**Decision**: Backend verifies JWTs issued by Better Auth using shared secret.

**Rationale**:
- Better Auth issues tokens on frontend
- Backend only needs to verify, not issue
- Shared secret (`BETTER_AUTH_SECRET` / `JWT_SECRET`) synchronizes both

**Implementation**:
```python
# Backend JWT verification
from jose import jwt, JWTError

def verify_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload
```

**Security Considerations**:
- Verify `exp` claim for expiration
- Verify `sub` claim for user identity
- Return 401 for invalid/expired tokens

### 7. API Design Pattern

**Decision**: RESTful API with resource-based endpoints.

**Rationale**:
- Constitution requires REST API
- Simple, well-understood pattern
- Easy to document and test

**Endpoint Structure**:
```
POST   /api/auth/verify     # Verify JWT (optional health check)
GET    /api/todos           # List user's todos
POST   /api/todos           # Create todo
GET    /api/todos/{id}      # Get specific todo
PUT    /api/todos/{id}      # Update todo
DELETE /api/todos/{id}      # Delete todo
```

### 8. User Data Isolation

**Decision**: Filter all queries by authenticated user's ID.

**Rationale**:
- Constitution V mandates user data isolation
- Prevents cross-user data access
- Simple and effective

**Implementation**:
```python
# All todo queries include user_id filter
async def get_todos(user_id: str, db: AsyncSession):
    result = await db.execute(
        select(Todo).where(Todo.user_id == user_id)
    )
    return result.scalars().all()
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
JWT_SECRET=shared-secret-with-frontend
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```
BETTER_AUTH_SECRET=shared-secret-with-backend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Unresolved Items

None - all technical decisions align with constitution requirements.

## References

- [Better Auth Documentation](https://www.better-auth.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon Documentation](https://neon.tech/docs/)
