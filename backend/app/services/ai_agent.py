"""
AI Agent Service - Uses OpenAI API with function calling for todo management.
This provides a stateless AI agent that can understand natural language and execute todo operations.
"""

import json
from typing import Optional, List, AsyncGenerator
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.services.todo_tools import (
    create_todo_tool,
    list_todos_tool,
    complete_todo_tool,
    uncomplete_todo_tool,
    delete_todo_tool,
    delete_completed_todos_tool,
    update_todo_tool,
    search_todos_tool,
)

settings = get_settings()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)

# Define the tools (functions) available to the AI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_todo",
            "description": "Create a new todo item. Use this when the user wants to add a new task, reminder, or item to their list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title or description of the todo item to create"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_todos",
            "description": "List all todos for the user. Use this when the user wants to see their tasks, view their list, or check what they have to do.",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_completed": {
                        "type": "boolean",
                        "description": "Whether to include completed todos in the list. Default is true.",
                        "default": True
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_todo",
            "description": "Mark a todo as completed/done. Use this when the user says they finished, completed, or done with a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_identifier": {
                        "type": "string",
                        "description": "The title (or part of it) or ID of the todo to mark as complete"
                    }
                },
                "required": ["todo_identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "uncomplete_todo",
            "description": "Mark a todo as not completed (reopen it). Use this when the user wants to undo completion or reopen a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_identifier": {
                        "type": "string",
                        "description": "The title (or part of it) or ID of the todo to mark as not complete"
                    }
                },
                "required": ["todo_identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_todo",
            "description": "Delete a specific todo item. Use this when the user wants to remove or delete a single task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_identifier": {
                        "type": "string",
                        "description": "The title (or part of it) or ID of the todo to delete"
                    }
                },
                "required": ["todo_identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_completed_todos",
            "description": "Delete all completed todos. Use this when the user wants to clear, remove, or clean up all their finished tasks.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_todo",
            "description": "Update or rename a todo's title. Use this when the user wants to change, edit, or rename a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_identifier": {
                        "type": "string",
                        "description": "The current title (or part of it) or ID of the todo to update"
                    },
                    "new_title": {
                        "type": "string",
                        "description": "The new title for the todo"
                    }
                },
                "required": ["todo_identifier", "new_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_todos",
            "description": "Search for todos by keyword. Use this when the user wants to find specific tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search keyword to find in todo titles"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a helpful AI assistant that helps users manage their todo list. You can:

1. **Create todos**: Add new tasks to the user's list
2. **List todos**: Show all tasks (can filter completed/incomplete)
3. **Complete todos**: Mark tasks as done
4. **Uncomplete todos**: Mark completed tasks as not done
5. **Delete todos**: Remove specific tasks
6. **Delete completed**: Clear all finished tasks
7. **Update todos**: Change/rename task titles
8. **Search todos**: Find tasks by keyword

When responding:
- Be friendly and concise
- Confirm actions you've taken
- If a todo operation fails or returns multiple matches, explain clearly
- Format todo lists nicely when showing them
- Use natural language, not technical jargon

If the user's request is not related to todo management, politely redirect them to todo-related tasks.

When showing todos, format them as a nice list like:
- [ ] Task name (for incomplete)
- [x] Task name (for completed)
"""


async def execute_tool(
    tool_name: str,
    arguments: dict,
    db: AsyncSession,
    user_id: str,
) -> dict:
    """Execute a tool and return the result."""
    if tool_name == "create_todo":
        return await create_todo_tool(db, user_id, arguments["title"])
    elif tool_name == "list_todos":
        include_completed = arguments.get("include_completed", True)
        return await list_todos_tool(db, user_id, include_completed)
    elif tool_name == "complete_todo":
        return await complete_todo_tool(db, user_id, arguments["todo_identifier"])
    elif tool_name == "uncomplete_todo":
        return await uncomplete_todo_tool(db, user_id, arguments["todo_identifier"])
    elif tool_name == "delete_todo":
        return await delete_todo_tool(db, user_id, arguments["todo_identifier"])
    elif tool_name == "delete_completed_todos":
        return await delete_completed_todos_tool(db, user_id)
    elif tool_name == "update_todo":
        return await update_todo_tool(
            db, user_id, arguments["todo_identifier"], arguments["new_title"]
        )
    elif tool_name == "search_todos":
        return await search_todos_tool(db, user_id, arguments["query"])
    else:
        return {"success": False, "message": f"Unknown tool: {tool_name}"}


async def chat_with_agent(
    user_message: str,
    conversation_history: List[dict],
    db: AsyncSession,
    user_id: str,
) -> tuple[str, List[dict]]:
    """
    Process a user message and return the AI response.

    Args:
        user_message: The user's message
        conversation_history: Previous messages in the conversation
        db: Database session
        user_id: The user's ID

    Returns:
        Tuple of (assistant_response, tool_calls_made)
    """
    # Build messages for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history (limit to last 20 messages for context)
    for msg in conversation_history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    tool_calls_made = []

    # Call OpenAI with tools
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    # Process tool calls if any
    while assistant_message.tool_calls:
        # Add assistant's response with tool calls to messages
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # Execute the tool
            result = await execute_tool(tool_name, arguments, db, user_id)

            tool_calls_made.append({
                "tool": tool_name,
                "arguments": arguments,
                "result": result
            })

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        # Get next response from OpenAI
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

    # Return the final response
    return assistant_message.content or "I'm sorry, I couldn't process that request.", tool_calls_made


async def chat_with_agent_stream(
    user_message: str,
    conversation_history: List[dict],
    db: AsyncSession,
    user_id: str,
) -> AsyncGenerator[str, None]:
    """
    Process a user message and stream the AI response.

    Args:
        user_message: The user's message
        conversation_history: Previous messages in the conversation
        db: Database session
        user_id: The user's ID

    Yields:
        Chunks of the assistant's response
    """
    # Build messages for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history
    for msg in conversation_history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # First, make a non-streaming call to handle tool calls
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    # Process tool calls if any (non-streaming)
    while assistant_message.tool_calls:
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            result = await execute_tool(tool_name, arguments, db, user_id)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

    # Now stream the final response
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages + [{"role": "assistant", "content": assistant_message.content or ""}],
        stream=True,
    )

    # If we already have the response from tool calls, yield it
    if assistant_message.content:
        yield assistant_message.content
    else:
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
