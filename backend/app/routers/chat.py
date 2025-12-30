"""
Chat Router - API endpoints for AI chat functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID
from datetime import datetime
from typing import List
import json

from app.database import get_db
from app.models.conversation import Conversation, Message
from app.schemas.conversation import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ConversationWithMessages,
    MessageResponse,
)
from app.services.auth import get_current_user
from app.services.ai_agent import chat_with_agent, chat_with_agent_stream

router = APIRouter()


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the authenticated user."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return conversations


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new conversation."""
    conversation = Conversation(
        user_id=user_id,
        title="New Chat",
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: UUID,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a conversation with all its messages."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get messages for this conversation
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = messages_result.scalars().all()

    # Parse tool_calls JSON for each message
    message_responses = []
    for msg in messages:
        msg_dict = {
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "role": msg.role,
            "content": msg.content,
            "tool_calls": msg.get_tool_calls(),
            "created_at": msg.created_at,
        }
        message_responses.append(MessageResponse(**msg_dict))

    return ConversationWithMessages(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=message_responses
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation and all its messages."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Delete all messages first
    messages_result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id)
    )
    messages = messages_result.scalars().all()
    for msg in messages:
        await db.delete(msg)

    # Delete the conversation
    await db.delete(conversation)
    await db.commit()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI assistant and get a response.
    Creates a new conversation if conversation_id is not provided.
    """
    # Get or create conversation
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            title="New Chat",
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Get conversation history
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    )
    history_messages = messages_result.scalars().all()

    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages
    ]

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # Get AI response
    try:
        assistant_response, tool_calls = await chat_with_agent(
            request.message,
            conversation_history,
            db,
            user_id,
        )
    except Exception as e:
        # If AI fails, still save an error message
        error_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=f"I'm sorry, I encountered an error: {str(e)}. Please try again.",
        )
        db.add(error_message)
        await db.commit()
        await db.refresh(error_message)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=assistant_response,
    )
    if tool_calls:
        assistant_msg.set_tool_calls(tool_calls)

    db.add(assistant_msg)

    # Update conversation title if it's the first message
    if len(history_messages) == 0:
        # Use first few words of user message as title
        title_words = request.message.split()[:5]
        conversation.title = " ".join(title_words) + ("..." if len(request.message.split()) > 5 else "")
        conversation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(assistant_msg)
    await db.refresh(conversation)

    return ChatResponse(
        conversation_id=conversation.id,
        message=MessageResponse(
            id=user_message.id,
            conversation_id=user_message.conversation_id,
            role=user_message.role,
            content=user_message.content,
            tool_calls=None,
            created_at=user_message.created_at,
        ),
        assistant_message=MessageResponse(
            id=assistant_msg.id,
            conversation_id=assistant_msg.conversation_id,
            role=assistant_msg.role,
            content=assistant_msg.content,
            tool_calls=assistant_msg.get_tool_calls(),
            created_at=assistant_msg.created_at,
        ),
    )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI assistant and get a streaming response.
    """
    # Get or create conversation
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        conversation = Conversation(
            user_id=user_id,
            title="New Chat",
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    # Get conversation history
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
    )
    history_messages = messages_result.scalars().all()

    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages
    ]

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    async def generate():
        full_response = ""
        try:
            async for chunk in chat_with_agent_stream(
                request.message,
                conversation_history,
                db,
                user_id,
            ):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk, 'conversation_id': str(conversation.id)})}\n\n"

            # Save assistant message after streaming completes
            assistant_msg = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_response,
            )
            db.add(assistant_msg)

            # Update conversation title if first message
            if len(history_messages) == 0:
                title_words = request.message.split()[:5]
                conversation.title = " ".join(title_words) + ("..." if len(request.message.split()) > 5 else "")
                conversation.updated_at = datetime.utcnow()

            await db.commit()

            yield f"data: {json.dumps({'done': True, 'conversation_id': str(conversation.id)})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
