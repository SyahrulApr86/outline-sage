from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from outline_sage_api.models import Conversation, Message


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(self, user_id: str) -> list[Conversation]:
        result = await self._session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_owned(self, conversation_id: uuid.UUID, user_id: str) -> Conversation | None:
        conversation = await self._session.get(Conversation, conversation_id)
        if conversation is None or conversation.user_id != user_id:
            return None
        return conversation

    async def get_or_create(self, conversation_id: uuid.UUID | None, user_id: str) -> Conversation:
        if conversation_id:
            conversation = await self.get_owned(conversation_id, user_id)
            if conversation:
                return conversation
        conversation = Conversation(user_id=user_id)
        self._session.add(conversation)
        await self._session.flush()
        return conversation

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        citations: list[dict] | None = None,
    ) -> Message:
        message = Message(conversation_id=conversation_id, role=role, content=content, citations=citations)
        self._session.add(message)
        await self._session.flush()
        return message

    async def list_messages(self, conversation_id: uuid.UUID) -> list[Message]:
        result = await self._session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())
