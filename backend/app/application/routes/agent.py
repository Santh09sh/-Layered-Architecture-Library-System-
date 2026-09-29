"""
Agent Routes
AI LibraryAI chat and tool endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.ai.agent import LibraryAgent
from app.application.schemas.common import AgentChatRequest, AgentChatResponse
from app.application.dependencies import get_current_user
from app.domain.entities.user import User

router = APIRouter(prefix="/api/agent", tags=["AI Agent"])


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(
    request: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = LibraryAgent(db, user_id=current_user.id)
    result = await agent.chat(request.message, request.conversation_history)
    return AgentChatResponse(**result)


@router.get("/tools")
async def list_tools(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = LibraryAgent(db, user_id=current_user.id)
    return {"tools": agent.get_available_tools()}
