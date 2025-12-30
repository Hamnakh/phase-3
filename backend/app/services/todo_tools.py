"""
Todo MCP Tools - Tool definitions for AI Agent to manage todos.
These are function tools that the OpenAI Agent can call to perform todo operations.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo


async def create_todo_tool(
    db: AsyncSession,
    user_id: str,
    title: str,
) -> dict:
    """
    Create a new todo item.

    Args:
        db: Database session
        user_id: The user's ID
        title: The title/description of the todo item

    Returns:
        dict with the created todo's details
    """
    todo = Todo(
        title=title.strip(),
        user_id=user_id,
    )
    db.add(todo)
    await db.commit()
    await db.refresh(todo)

    return {
        "success": True,
        "todo": {
            "id": str(todo.id),
            "title": todo.title,
            "completed": todo.completed,
            "created_at": todo.created_at.isoformat(),
        },
        "message": f"Created todo: '{todo.title}'"
    }


async def list_todos_tool(
    db: AsyncSession,
    user_id: str,
    include_completed: bool = True,
) -> dict:
    """
    List all todos for the user.

    Args:
        db: Database session
        user_id: The user's ID
        include_completed: Whether to include completed todos (default: True)

    Returns:
        dict with list of todos
    """
    query = select(Todo).where(Todo.user_id == user_id)

    if not include_completed:
        query = query.where(Todo.completed == False)

    query = query.order_by(Todo.created_at.desc())

    result = await db.execute(query)
    todos = result.scalars().all()

    todo_list = [
        {
            "id": str(todo.id),
            "title": todo.title,
            "completed": todo.completed,
            "created_at": todo.created_at.isoformat(),
        }
        for todo in todos
    ]

    return {
        "success": True,
        "todos": todo_list,
        "total": len(todo_list),
        "message": f"Found {len(todo_list)} todo(s)"
    }


async def complete_todo_tool(
    db: AsyncSession,
    user_id: str,
    todo_identifier: str,
) -> dict:
    """
    Mark a todo as completed by title (partial match) or ID.

    Args:
        db: Database session
        user_id: The user's ID
        todo_identifier: The todo title (partial match) or ID

    Returns:
        dict with the result
    """
    # First try to find by exact ID
    try:
        todo_id = UUID(todo_identifier)
        result = await db.execute(
            select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        )
        todo = result.scalar_one_or_none()
    except (ValueError, AttributeError):
        todo = None

    # If not found by ID, search by title (case-insensitive partial match)
    if not todo:
        result = await db.execute(
            select(Todo).where(
                Todo.user_id == user_id,
                Todo.title.ilike(f"%{todo_identifier}%")
            )
        )
        todos = result.scalars().all()

        if len(todos) == 0:
            return {
                "success": False,
                "message": f"No todo found matching '{todo_identifier}'"
            }
        elif len(todos) > 1:
            matches = [{"id": str(t.id), "title": t.title} for t in todos]
            return {
                "success": False,
                "message": f"Multiple todos match '{todo_identifier}'. Please be more specific.",
                "matches": matches
            }
        else:
            todo = todos[0]

    if todo.completed:
        return {
            "success": True,
            "message": f"Todo '{todo.title}' is already completed",
            "todo": {
                "id": str(todo.id),
                "title": todo.title,
                "completed": True,
            }
        }

    todo.completed = True
    todo.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(todo)

    return {
        "success": True,
        "message": f"Marked '{todo.title}' as completed",
        "todo": {
            "id": str(todo.id),
            "title": todo.title,
            "completed": todo.completed,
        }
    }


async def uncomplete_todo_tool(
    db: AsyncSession,
    user_id: str,
    todo_identifier: str,
) -> dict:
    """
    Mark a todo as not completed (uncomplete) by title (partial match) or ID.

    Args:
        db: Database session
        user_id: The user's ID
        todo_identifier: The todo title (partial match) or ID

    Returns:
        dict with the result
    """
    # First try to find by exact ID
    try:
        todo_id = UUID(todo_identifier)
        result = await db.execute(
            select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        )
        todo = result.scalar_one_or_none()
    except (ValueError, AttributeError):
        todo = None

    # If not found by ID, search by title
    if not todo:
        result = await db.execute(
            select(Todo).where(
                Todo.user_id == user_id,
                Todo.title.ilike(f"%{todo_identifier}%")
            )
        )
        todos = result.scalars().all()

        if len(todos) == 0:
            return {
                "success": False,
                "message": f"No todo found matching '{todo_identifier}'"
            }
        elif len(todos) > 1:
            matches = [{"id": str(t.id), "title": t.title} for t in todos]
            return {
                "success": False,
                "message": f"Multiple todos match '{todo_identifier}'. Please be more specific.",
                "matches": matches
            }
        else:
            todo = todos[0]

    if not todo.completed:
        return {
            "success": True,
            "message": f"Todo '{todo.title}' is not completed yet",
            "todo": {
                "id": str(todo.id),
                "title": todo.title,
                "completed": False,
            }
        }

    todo.completed = False
    todo.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(todo)

    return {
        "success": True,
        "message": f"Marked '{todo.title}' as not completed",
        "todo": {
            "id": str(todo.id),
            "title": todo.title,
            "completed": todo.completed,
        }
    }


async def delete_todo_tool(
    db: AsyncSession,
    user_id: str,
    todo_identifier: str,
) -> dict:
    """
    Delete a todo by title (partial match) or ID.

    Args:
        db: Database session
        user_id: The user's ID
        todo_identifier: The todo title (partial match) or ID

    Returns:
        dict with the result
    """
    # First try to find by exact ID
    try:
        todo_id = UUID(todo_identifier)
        result = await db.execute(
            select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        )
        todo = result.scalar_one_or_none()
    except (ValueError, AttributeError):
        todo = None

    # If not found by ID, search by title
    if not todo:
        result = await db.execute(
            select(Todo).where(
                Todo.user_id == user_id,
                Todo.title.ilike(f"%{todo_identifier}%")
            )
        )
        todos = result.scalars().all()

        if len(todos) == 0:
            return {
                "success": False,
                "message": f"No todo found matching '{todo_identifier}'"
            }
        elif len(todos) > 1:
            matches = [{"id": str(t.id), "title": t.title} for t in todos]
            return {
                "success": False,
                "message": f"Multiple todos match '{todo_identifier}'. Please be more specific.",
                "matches": matches
            }
        else:
            todo = todos[0]

    title = todo.title
    await db.delete(todo)
    await db.commit()

    return {
        "success": True,
        "message": f"Deleted todo: '{title}'"
    }


async def delete_completed_todos_tool(
    db: AsyncSession,
    user_id: str,
) -> dict:
    """
    Delete all completed todos for the user.

    Args:
        db: Database session
        user_id: The user's ID

    Returns:
        dict with the result
    """
    result = await db.execute(
        select(Todo).where(
            Todo.user_id == user_id,
            Todo.completed == True
        )
    )
    completed_todos = result.scalars().all()

    if not completed_todos:
        return {
            "success": True,
            "message": "No completed todos to delete",
            "deleted_count": 0
        }

    count = len(completed_todos)
    for todo in completed_todos:
        await db.delete(todo)
    await db.commit()

    return {
        "success": True,
        "message": f"Deleted {count} completed todo(s)",
        "deleted_count": count
    }


async def update_todo_tool(
    db: AsyncSession,
    user_id: str,
    todo_identifier: str,
    new_title: str,
) -> dict:
    """
    Update a todo's title by finding it by title (partial match) or ID.

    Args:
        db: Database session
        user_id: The user's ID
        todo_identifier: The todo title (partial match) or ID to find
        new_title: The new title for the todo

    Returns:
        dict with the result
    """
    # First try to find by exact ID
    try:
        todo_id = UUID(todo_identifier)
        result = await db.execute(
            select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        )
        todo = result.scalar_one_or_none()
    except (ValueError, AttributeError):
        todo = None

    # If not found by ID, search by title
    if not todo:
        result = await db.execute(
            select(Todo).where(
                Todo.user_id == user_id,
                Todo.title.ilike(f"%{todo_identifier}%")
            )
        )
        todos = result.scalars().all()

        if len(todos) == 0:
            return {
                "success": False,
                "message": f"No todo found matching '{todo_identifier}'"
            }
        elif len(todos) > 1:
            matches = [{"id": str(t.id), "title": t.title} for t in todos]
            return {
                "success": False,
                "message": f"Multiple todos match '{todo_identifier}'. Please be more specific.",
                "matches": matches
            }
        else:
            todo = todos[0]

    old_title = todo.title
    todo.title = new_title.strip()
    todo.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(todo)

    return {
        "success": True,
        "message": f"Updated '{old_title}' to '{todo.title}'",
        "todo": {
            "id": str(todo.id),
            "title": todo.title,
            "completed": todo.completed,
        }
    }


async def search_todos_tool(
    db: AsyncSession,
    user_id: str,
    query: str,
) -> dict:
    """
    Search todos by keyword in title.

    Args:
        db: Database session
        user_id: The user's ID
        query: Search keyword

    Returns:
        dict with matching todos
    """
    result = await db.execute(
        select(Todo).where(
            Todo.user_id == user_id,
            Todo.title.ilike(f"%{query}%")
        ).order_by(Todo.created_at.desc())
    )
    todos = result.scalars().all()

    todo_list = [
        {
            "id": str(todo.id),
            "title": todo.title,
            "completed": todo.completed,
            "created_at": todo.created_at.isoformat(),
        }
        for todo in todos
    ]

    return {
        "success": True,
        "todos": todo_list,
        "total": len(todo_list),
        "message": f"Found {len(todo_list)} todo(s) matching '{query}'"
    }
