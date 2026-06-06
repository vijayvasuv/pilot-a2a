"""FastAPI chat gateway — runs the A2A router agent via ADK Runner."""

import json
import os
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field

from router.agent import root_agent

APP_NAME = "a2a_support_pilot"
runner: Runner | None = None
session_service: InMemorySessionService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global runner, session_service
    session_service = InMemorySessionService()
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )
    yield


app = FastAPI(
    title="A2A Support Pilot",
    description="Chat API routing to login/billing specialists via A2A",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    user_id: str = "user"


class ChatResponse(BaseModel):
    session_id: str
    reply: str


def _extract_text_from_event(event) -> str | None:
    if not event.content or not event.content.parts:
        return None
    texts = []
    for part in event.content.parts:
        if hasattr(part, "text") and part.text:
            texts.append(part.text)
    return "\n".join(texts) if texts else None


@app.get("/health")
async def health():
    return {"status": "ok", "app": APP_NAME}


@app.get("/")
async def chat_ui():
    ui_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(ui_path):
        return FileResponse(ui_path)
    return {"message": "Chat UI not found. Use POST /chat"}


def _friendly_error(exc: Exception) -> str:
    msg = str(exc)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
        return (
            "The AI service rate limit was reached (Gemini free tier). "
            "Please wait about 1 minute and try again. "
            "Tip: use fewer messages per session, or wait until tomorrow for quota reset."
        )
    if "503" in msg or "connection" in msg.lower() or "refused" in msg.lower():
        return (
            "Could not reach a specialist agent. Please ensure all services are running "
            "(ports 8001–8003) and try again."
        )
    return f"Something went wrong while processing your message. Please try again. ({type(exc).__name__})"


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if runner is None or session_service is None:
        raise HTTPException(status_code=503, detail="Agent runner not initialized")

    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id

    existing = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    if existing is None:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )

    user_content = types.Content(
        role="user",
        parts=[types.Part(text=request.message)],
    )

    final_reply = ""
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content,
        ):
            if event.author == "user":
                continue
            text = _extract_text_from_event(event)
            if text:
                final_reply = text
    except Exception as exc:
        return ChatResponse(session_id=session_id, reply=_friendly_error(exc))

    if not final_reply:
        final_reply = (
            "I'm processing your request. Please ensure specialist agents are running "
            "(ports 8001–8003) and try again."
        )

    return ChatResponse(session_id=session_id, reply=final_reply)


_REGISTRY_PATH = Path(__file__).parent.parent / "router" / "registry.json"


@app.get("/registry")
async def registry():
    return json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
