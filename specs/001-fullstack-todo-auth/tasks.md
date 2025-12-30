# Tasks: Full-Stack Todo App with Authentication

**Input**: Design documents from `/specs/001-fullstack-todo-auth/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml

**Tests**: Not requested in specification - skipping test tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/src/`
- Backend: FastAPI + SQLModel + Python 3.11
- Frontend: Next.js 14 (App Router) + TypeScript + Better Auth

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend project structure with directories: app/, app/models/, app/routers/, app/services/, app/schemas/, tests/
- [x] T002 [P] Initialize backend Python project with requirements.txt (fastapi, uvicorn, sqlmodel, python-jose, asyncpg, python-dotenv)
- [x] T003 [P] Create frontend Next.js 14 project with App Router in frontend/
- [x] T004 [P] Create backend/.env.example with DATABASE_URL, JWT_SECRET, CORS_ORIGINS placeholders
- [x] T005 [P] Create frontend/.env.example with BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL placeholders

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create environment configuration in backend/app/config.py (load from .env)
- [x] T007 Create database connection and session management in backend/app/database.py (async SQLModel with Neon PostgreSQL)
- [x] T008 [P] Create User SQLModel in backend/app/models/user.py per data-model.md
- [x] T009 [P] Create Todo SQLModel in backend/app/models/todo.py per data-model.md
- [x] T010 Create models __init__.py exporting User and Todo in backend/app/models/__init__.py
- [x] T011 Create JWT verification service in backend/app/services/auth.py (get_current_user dependency)
- [x] T012 Create FastAPI app entry point in backend/app/main.py with CORS middleware and router includes
- [x] T013 Create health check endpoint in backend/app/routers/health.py (GET /api/health)
- [x] T014 [P] Create TypeScript interfaces in frontend/src/types/index.ts per data-model.md (User, Todo, CreateTodoRequest, UpdateTodoRequest)
- [x] T015 [P] Configure Better Auth client in frontend/src/lib/auth.ts
- [x] T016 Create API client with JWT attachment in frontend/src/lib/api.ts
- [x] T017 Create root layout with Better Auth provider in frontend/src/app/layout.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration (Priority: P1)

**Goal**: Allow new users to create accounts with email and password

**Independent Test**: Complete signup flow, verify user can subsequently log in

### Implementation for User Story 1

- [x] T018 [US1] Create user Pydantic schemas in backend/app/schemas/user.py (UserCreate, UserResponse)
- [x] T019 [US1] Create SignupForm component in frontend/src/components/auth/SignupForm.tsx with email/password validation (min 8 chars)
- [x] T020 [US1] Create signup page in frontend/src/app/(auth)/signup/page.tsx using SignupForm
- [x] T021 [US1] Configure Better Auth signup handler to create user and issue JWT
- [x] T022 [US1] Add user sync endpoint in backend to create user record on first API call (or via webhook)

**Checkpoint**: User Story 1 complete - users can register

---

## Phase 4: User Story 2 - User Login/Logout (Priority: P1)

**Goal**: Allow registered users to log in and out securely

**Independent Test**: Log in with valid credentials, access dashboard, logout, verify access revoked

### Implementation for User Story 2

- [x] T023 [US2] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx with email/password fields
- [x] T024 [US2] Create login page in frontend/src/app/(auth)/login/page.tsx using LoginForm
- [x] T025 [US2] Configure Better Auth login handler to verify credentials and issue JWT
- [x] T026 [US2] Add logout functionality in frontend/src/lib/auth.ts
- [x] T027 [US2] Create protected layout in frontend/src/app/(protected)/layout.tsx that redirects unauthenticated users to /login
- [x] T028 [US2] Create landing page in frontend/src/app/page.tsx that redirects to /todos if logged in, else /login

**Checkpoint**: User Stories 1 & 2 complete - full auth flow working

---

## Phase 5: User Story 3 - Create Todo (Priority: P2)

**Goal**: Allow authenticated users to create new todo items

**Independent Test**: Add a new todo, verify it appears in the list

### Implementation for User Story 3

- [x] T029 [US3] Create todo Pydantic schemas in backend/app/schemas/todo.py (TodoCreate, TodoUpdate, TodoResponse)
- [x] T030 [US3] Create POST /api/todos endpoint in backend/app/routers/todos.py (requires auth, creates todo with user_id)
- [x] T031 [US3] Create TodoForm component in frontend/src/components/todos/TodoForm.tsx with title input and submit
- [x] T032 [US3] Add createTodo function in frontend/src/lib/api.ts (POST to /api/todos with JWT)

**Checkpoint**: User Story 3 complete - users can create todos

---

## Phase 6: User Story 4 - View My Todos (Priority: P2)

**Goal**: Allow authenticated users to view all their todos

**Independent Test**: Create multiple todos, verify all appear in list (newest first), verify other users' todos not visible

### Implementation for User Story 4

- [x] T033 [US4] Create GET /api/todos endpoint in backend/app/routers/todos.py (requires auth, filters by user_id, orders by created_at DESC)
- [x] T034 [US4] Create TodoItem component in frontend/src/components/todos/TodoItem.tsx displaying title and completion status
- [x] T035 [US4] Create TodoList component in frontend/src/components/todos/TodoList.tsx rendering list of TodoItems with empty state
- [x] T036 [US4] Add fetchTodos function in frontend/src/lib/api.ts (GET /api/todos with JWT)
- [x] T037 [US4] Create todos page in frontend/src/app/(protected)/todos/page.tsx with TodoList and TodoForm

**Checkpoint**: User Stories 3 & 4 complete - users can create and view todos

---

## Phase 7: User Story 5 - Update Todo (Priority: P3)

**Goal**: Allow authenticated users to edit todo titles

**Independent Test**: Edit a todo's title, verify change persists

### Implementation for User Story 5

- [x] T038 [US5] Create PUT /api/todos/{id} endpoint in backend/app/routers/todos.py (requires auth, verifies ownership, updates title)
- [x] T039 [US5] Add edit mode to TodoItem component in frontend/src/components/todos/TodoItem.tsx with inline editing
- [x] T040 [US5] Add updateTodo function in frontend/src/lib/api.ts (PUT to /api/todos/{id} with JWT)
- [x] T041 [US5] Add validation to prevent empty title on update (frontend and backend)

**Checkpoint**: User Story 5 complete - users can edit todos

---

## Phase 8: User Story 6 - Mark Todo Complete/Incomplete (Priority: P3)

**Goal**: Allow authenticated users to toggle todo completion status

**Independent Test**: Toggle todo status, verify visual feedback and persistence

### Implementation for User Story 6

- [x] T042 [US6] Update PUT /api/todos/{id} endpoint in backend/app/routers/todos.py to handle completed field update
- [x] T043 [US6] Add checkbox/toggle to TodoItem component in frontend/src/components/todos/TodoItem.tsx for completion status
- [x] T044 [US6] Add toggleTodoComplete function in frontend/src/lib/api.ts using updateTodo
- [x] T045 [US6] Add visual styling for completed todos (strikethrough, dimmed, etc.)

**Checkpoint**: User Story 6 complete - users can mark todos complete/incomplete

---

## Phase 9: User Story 7 - Delete Todo (Priority: P3)

**Goal**: Allow authenticated users to delete their todos

**Independent Test**: Delete a todo, verify it no longer appears in list

### Implementation for User Story 7

- [x] T046 [US7] Create DELETE /api/todos/{id} endpoint in backend/app/routers/todos.py (requires auth, verifies ownership)
- [x] T047 [US7] Add delete button to TodoItem component in frontend/src/components/todos/TodoItem.tsx
- [x] T048 [US7] Add deleteTodo function in frontend/src/lib/api.ts (DELETE /api/todos/{id} with JWT)
- [x] T049 [US7] Add confirmation or undo capability for delete action (optional UX improvement)

**Checkpoint**: All user stories complete - full CRUD functionality

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T050 [P] Add error handling middleware in backend/app/main.py for consistent error responses
- [x] T051 [P] Add loading states to frontend components (TodoList, forms)
- [x] T052 [P] Add toast notifications for success/error feedback in frontend
- [x] T053 Verify all API endpoints return proper HTTP status codes per OpenAPI contract
- [x] T054 [P] Add responsive styling for mobile devices
- [ ] T055 Run quickstart.md validation - test full flow end-to-end
- [x] T056 Security review: verify user isolation, JWT validation, no data leakage

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1 & US2 (auth) should complete before US3-US7 (todo operations)
  - US3 & US4 (create/view) can run in parallel
  - US5, US6, US7 (update/toggle/delete) can run in parallel after US4
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Registration)**: Can start after Foundational - No dependencies
- **US2 (Login/Logout)**: Can start after Foundational - No dependencies on US1 but shares auth components
- **US3 (Create Todo)**: Requires US1/US2 complete (needs auth working)
- **US4 (View Todos)**: Requires US3 complete (needs todos to exist to view)
- **US5 (Update Todo)**: Requires US4 complete (needs list view)
- **US6 (Toggle Complete)**: Requires US4 complete (needs list view)
- **US7 (Delete Todo)**: Requires US4 complete (needs list view)

### Within Each User Story

- Backend before frontend (API must exist before UI calls it)
- Schemas before endpoints
- Core implementation before validation/polish

### Parallel Opportunities

- T002, T003, T004, T005 (Setup) can run in parallel
- T008, T009, T014, T015 (Foundational models/types) can run in parallel
- US3 and US4 implementation can run in parallel once auth is done
- US5, US6, US7 can all run in parallel after US4
- All Phase 10 tasks marked [P] can run in parallel

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all model/type tasks together:
Task: "Create User SQLModel in backend/app/models/user.py"
Task: "Create Todo SQLModel in backend/app/models/todo.py"
Task: "Create TypeScript interfaces in frontend/src/types/index.ts"
Task: "Configure Better Auth client in frontend/src/lib/auth.ts"
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3 + US4)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Registration (US1)
4. Complete Phase 4: User Login/Logout (US2)
5. Complete Phase 5: Create Todo (US3)
6. Complete Phase 6: View Todos (US4)
7. **STOP and VALIDATE**: Users can register, login, create and view todos
8. Deploy/demo MVP

### Full Feature Delivery

1. Complete MVP (above)
2. Add US5: Update Todo
3. Add US6: Toggle Complete
4. Add US7: Delete Todo
5. Complete Phase 10: Polish
6. Final validation with quickstart.md

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Backend uses FastAPI patterns: routers, services, schemas, models
- Frontend uses Next.js App Router with (auth) and (protected) route groups
- Better Auth handles JWT issuance; backend only verifies
- All todo queries MUST filter by user_id (Constitution V)
- Commit after each task or logical group
