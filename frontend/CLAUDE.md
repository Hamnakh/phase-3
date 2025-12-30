# Frontend Development Guidelines

Auto-generated from feature plans. Last updated: 2025-12-27

## Active Technologies

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.x
- **Authentication**: Better Auth
- **Styling**: Tailwind CSS (recommended)
- **State Management**: React hooks / Server Components

## Project Structure

```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout with auth provider
│   │   ├── page.tsx             # Landing/redirect
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   └── (protected)/
│   │       └── todos/page.tsx   # Main todo list
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── SignupForm.tsx
│   │   └── todos/
│   │       ├── TodoList.tsx
│   │       ├── TodoItem.tsx
│   │       └── TodoForm.tsx
│   ├── lib/
│   │   ├── auth.ts              # Better Auth client
│   │   └── api.ts               # API client with JWT
│   └── types/
│       └── index.ts             # TypeScript interfaces
├── package.json
├── tsconfig.json
├── next.config.js
└── .env.local
```

## Commands

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint
npm run lint
```

## Code Style

### TypeScript
- Use strict mode
- Prefer interfaces over types for object shapes
- Use `async/await` over `.then()`

### React/Next.js
- Use Server Components by default
- Use `'use client'` only when needed
- Prefer named exports for components

### Authentication
- Better Auth handles all auth flows
- JWT stored in HTTP-only cookies
- Attach JWT to all API calls via `Authorization: Bearer <token>`

## Environment Variables

Required in `.env.local`:

```env
BETTER_AUTH_SECRET=<shared-secret-with-backend>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Key Patterns

### API Client with JWT

```typescript
// lib/api.ts
import { auth } from './auth';

export async function apiClient(endpoint: string, options: RequestInit = {}) {
  const session = await auth.getSession();

  return fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session?.token}`,
      ...options.headers,
    },
  });
}
```

### Protected Route

```typescript
// app/(protected)/layout.tsx
import { redirect } from 'next/navigation';
import { auth } from '@/lib/auth';

export default async function ProtectedLayout({ children }) {
  const session = await auth.getSession();

  if (!session) {
    redirect('/login');
  }

  return <>{children}</>;
}
```

## Recent Changes

- 001-fullstack-todo-auth: Initial setup with Better Auth, todo CRUD UI

<!-- MANUAL ADDITIONS START -->
<!-- Add any manual overrides or notes below this line -->
<!-- MANUAL ADDITIONS END -->
