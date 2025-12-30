# Implementation Plan: Full-Stack Todo App with Authentication

**Branch**: `001-fullstack-todo-auth` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fullstack-todo-auth/spec.md`

## Summary

Build a secure, multi-user todo application with JWT-based authentication. Users can register, login, and manage their personal todo lists with full CRUD operations. The system enforces strict user data isolation - each user can only access their own todos.

**Technical Approach**: Next.js frontend with Better Auth for authentication, FastAPI backend with SQLModel ORM, Neon Serverless PostgreSQL for persistence. JWT tokens secure all API communications.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Better Auth, Next.js 14 (App Router)
**Storage**: Neon Serverless PostgreSQL
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web browsers (desktop/mobile responsive)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <5s page load, <200ms API response, 100 concurrent users
**Constraints**: JWT token expiry 24h, password min 8 chars, email unique per user
**Scale/Scope**: MVP for hackathon, single-tenant, ~100 users initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Specs First | PASS | Spec created at `/specs/001-fullstack-todo-auth/spec.md` |
| II. Claude Code Builds | PASS | All implementation via Claude Code |
| III. Specs Are Source of Truth | PASS | Plan references spec, not vice versa |
| IV. Monorepo Required | PASS | Structure: `frontend/`, `backend/`, `specs/` |
| V. Security Mandatory | PASS | JWT auth, user data isolation via `user_id` |

**Architecture Compliance:**
- Frontend: Next.js (App Router) with Better Auth
- Backend: FastAPI with SQLModel ORM
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth issues JWT, backend verifies with shared secret

## Project Structure

### Documentation (this feature)

```text
specs/001-fullstack-todo-auth/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API specs)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

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
│   │   ├── auth.py          # Auth endpoints (verify JWT)
│   │   └── todos.py         # Todo CRUD endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth.py          # JWT verification service
│   └── schemas/
│       ├── __init__.py
│       ├── todo.py          # Pydantic schemas for todos
│       └── user.py          # Pydantic schemas for users
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_todos.py
├── requirements.txt
└── .env.example

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout with auth provider
│   │   ├── page.tsx         # Landing/redirect
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   └── (protected)/
│   │       └── todos/
│   │           └── page.tsx # Main todo list page
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── SignupForm.tsx
│   │   └── todos/
│   │       ├── TodoList.tsx
│   │       ├── TodoItem.tsx
│   │       └── TodoForm.tsx
│   ├── lib/
│   │   ├── auth.ts          # Better Auth client setup
│   │   └── api.ts           # API client with JWT attachment
│   └── types/
│       └── index.ts         # TypeScript interfaces
├── package.json
├── tsconfig.json
├── next.config.js
└── .env.example
```

**Structure Decision**: Web application structure selected per Constitution IV. Frontend and backend in separate directories with clear separation of concerns.

## Complexity Tracking

> No violations - all choices align with constitution requirements.

| Decision | Rationale |
|----------|-----------|
| Better Auth for frontend | Constitution mandates Better Auth for authentication |
| FastAPI backend | Constitution mandates FastAPI with SQLModel |
| JWT verification only in backend | Better Auth handles issuance; backend only verifies |
| Neon PostgreSQL | Constitution mandates Neon Serverless PostgreSQL |
