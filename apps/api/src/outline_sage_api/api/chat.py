"""Endpoint chat streaming dan riwayat percakapan (TSD-002 bagian 5, FSD-002, FSD-004)."""
from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from fastapi.responses import StreamingResponse

from outline_sage_api.auth import KeycloakAuthenticator
from outline_sage_api.citations import extract_citations
from outline_sage_api.conversations import ConversationRepository
from outline_sage_api.prompt import build_messages
from outline_sage_api.retrieval import HybridRetriever

chat_router = APIRouter()


async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = auth_header[len("Bearer ") :]
    authenticator: KeycloakAuthenticator = request.app.state.authenticator
    try:
        payload = await authenticator.verify(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return {"id": payload["sub"]}


@chat_router.get("/api/conversations")
async def list_conversations(request: Request, user: dict = Depends(get_current_user)):
    async with request.app.state.session_factory() as session:
        repo = ConversationRepository(session)
        conversations = await repo.list_for_user(user["id"])
        return [
            {"id": str(c.id), "title": c.title, "created_at": c.created_at.isoformat()}
            for c in conversations
        ]


@chat_router.get("/api/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: uuid.UUID, request: Request, user: dict = Depends(get_current_user)
):
    async with request.app.state.session_factory() as session:
        repo = ConversationRepository(session)
        conversation = await repo.get_owned(conversation_id, user["id"])
        if conversation is None:
            raise HTTPException(status_code=403, detail="not your conversation")
        messages = await repo.list_messages(conversation_id)
        return [
            {"role": m.role, "content": m.content, "citations": m.citations} for m in messages
        ]


@chat_router.post("/api/chat")
async def chat(request: Request, user: dict = Depends(get_current_user)):
    body = await request.json()
    query = body["message"]
    raw_conversation_id = body.get("conversation_id")
    conversation_id = uuid.UUID(raw_conversation_id) if raw_conversation_id else None

    retriever: HybridRetriever = request.app.state.retriever
    llm_client = request.app.state.llm_client
    session_factory = request.app.state.session_factory

    chunks = await retriever.retrieve(query)
    messages, chunk_map = build_messages(query, chunks)

    async def event_stream():
        answer_parts: list[str] = []
        async for token in llm_client.stream_chat(messages):
            answer_parts.append(token)
            yield f"data: {json.dumps({'type': 'text-delta', 'delta': token})}\n\n"

        full_answer = "".join(answer_parts)
        citations = extract_citations(full_answer, chunk_map)
        yield f"data: {json.dumps({'type': 'data-citation', 'citations': citations})}\n\n"
        yield "data: [DONE]\n\n"

        async with session_factory() as session:
            async with session.begin():
                repo = ConversationRepository(session)
                conversation = await repo.get_or_create(conversation_id, user["id"])
                await repo.add_message(conversation.id, "user", query)
                await repo.add_message(conversation.id, "assistant", full_answer, citations)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
