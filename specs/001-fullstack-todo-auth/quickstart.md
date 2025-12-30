# Quickstart: Full-Stack Todo App with Authentication

**Feature**: 001-fullstack-todo-auth
**Date**: 2025-12-27

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL database (Neon Serverless recommended)
- Git

## Quick Setup

### 1. Clone and Navigate

```bash
cd hackathon-todo
git checkout 001-fullstack-todo-auth
```

### 2. Environment Configuration

#### Backend (.env)

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/database?sslmode=require
JWT_SECRET=your-shared-secret-min-32-chars
CORS_ORIGINS=http://localhost:3000
```

#### Frontend (.env.local)

Create `frontend/.env.local`:

```env
BETTER_AUTH_SECRET=your-shared-secret-min-32-chars
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Important**: `JWT_SECRET` and `BETTER_AUTH_SECRET` MUST be the same value!

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: http://localhost:3000

## Verification Steps

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/health
# Expected: {"status": "healthy"}
```

### 2. Check API Docs

Open: http://localhost:8000/docs

You should see the Swagger UI with all endpoints.

### 3. Test User Flow

1. Open http://localhost:3000
2. Click "Sign Up"
3. Enter email and password (min 8 chars)
4. Should redirect to todo list
5. Add a todo
6. Refresh page - todo should persist
7. Log out
8. Log back in - todo should still be there

### 4. Test User Isolation

1. Create User A and add a todo
2. Log out
3. Create User B
4. User B should see empty todo list (not User A's todos)

## Common Issues

### CORS Errors

Ensure `CORS_ORIGINS` in backend `.env` includes the frontend URL:

```env
CORS_ORIGINS=http://localhost:3000
```

### JWT Verification Fails

Ensure both secrets match exactly:
- Backend: `JWT_SECRET`
- Frontend: `BETTER_AUTH_SECRET`

### Database Connection Fails

1. Check `DATABASE_URL` format
2. Ensure SSL mode is correct for Neon: `?sslmode=require`
3. Verify credentials are correct

### 401 on All Requests

1. Check if JWT token is being sent in `Authorization` header
2. Verify token format: `Bearer <token>`
3. Check if token has expired

## API Quick Reference

All endpoints require `Authorization: Bearer <token>` header (except health check).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Health check |
| GET | /api/todos | List user's todos |
| POST | /api/todos | Create todo |
| GET | /api/todos/{id} | Get todo |
| PUT | /api/todos/{id} | Update todo |
| DELETE | /api/todos/{id} | Delete todo |

## Next Steps

After basic setup works:

1. Run tests: `pytest` (backend), `npm test` (frontend)
2. Review the full [API contract](./contracts/openapi.yaml)
3. Check [data model](./data-model.md) for entity details
4. See [tasks.md](./tasks.md) for implementation checklist (after running `/speckit.tasks`)
