from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.api.v1.schemas.chat import ChatRequest, StructuredChatResponse
from app.services.gemini_service import GeminiService
from app.services.agent_service import AgentService
from app.services.mcp_service import MCPService
from app.services.memory_service import MemoryService
from app.infrastructure.database import get_db
from app.core.config import settings
from app.core.logger import logger

router = APIRouter()

async def get_agent_service(db: AsyncSession = Depends(get_db)) -> AgentService:
    gemini = GeminiService()
    mcp = MCPService()
    memory = MemoryService(db)
    return AgentService(gemini, mcp, memory)

@router.post("/chat", response_model=StructuredChatResponse)
async def chat(
    request: ChatRequest, 
    agent: AgentService = Depends(get_agent_service)
):
    """
    Primary endpoint returning a structured, frontend-ready mentor response.
    """
    session_id = request.session_id or str(uuid.uuid4())
    user_id = session_id 
    
    logger.info(f"Structured chat request for user: {user_id}")
    
    try:
        # Returns a StructuredChatResponse Pydantic model
        return await agent.process_message(
            user_id=user_id,
            session_id=session_id,
            message=request.message
        )
    except Exception as e:
        logger.error(f"Agent Orchestration Failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The mentor encountered a reasoning error. Please check the logs."
        )

@router.get("/health")
async def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
