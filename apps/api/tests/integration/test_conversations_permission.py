"""Integration test permission conversation: FSD-002 AC-7."""
from __future__ import annotations

import uuid

import pytest

from outline_sage_api.conversations import ConversationRepository


@pytest.mark.asyncio
async def test_user_cannot_access_conversation_owned_by_another_user(session_factory):
    owner_id = f"user-owner-{uuid.uuid4()}"
    stranger_id = f"user-stranger-{uuid.uuid4()}"

    async with session_factory() as session:
        async with session.begin():
            repo = ConversationRepository(session)
            conversation = await repo.get_or_create(None, owner_id)
            conversation_id = conversation.id

    async with session_factory() as session:
        repo = ConversationRepository(session)
        as_owner = await repo.get_owned(conversation_id, owner_id)
        as_stranger = await repo.get_owned(conversation_id, stranger_id)

    assert as_owner is not None
    assert as_stranger is None


@pytest.mark.asyncio
async def test_list_for_user_only_returns_own_conversations(session_factory):
    user_a = f"user-a-{uuid.uuid4()}"
    user_b = f"user-b-{uuid.uuid4()}"

    async with session_factory() as session:
        async with session.begin():
            repo = ConversationRepository(session)
            await repo.get_or_create(None, user_a)
            await repo.get_or_create(None, user_a)
            await repo.get_or_create(None, user_b)

    async with session_factory() as session:
        repo = ConversationRepository(session)
        user_a_conversations = await repo.list_for_user(user_a)

    assert len(user_a_conversations) == 2
    assert all(c.user_id == user_a for c in user_a_conversations)
