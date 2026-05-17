from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.memory_repository import MemoryRepository, UserRepository
from app.core.logger import logger
from datetime import datetime

class MemoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.memory_repo = MemoryRepository(session)
        self.user_repo = UserRepository(session)

    async def record_interaction(self, user_id: str, interaction_content: str):
        """
        Main logic to process a new interaction and store useful snippets.
        In production, this could be triggered by an LLM parsing the chat.
        """
        logger.info(f"Recording interaction memory for user: {user_id}")
        await self.user_repo.get_or_create_user(user_id)
        
        # Simple implementation for now. 
        # Future: Use LLM to extract key concepts instead of full raw messages.
        await self.memory_repo.add_memory(user_id, interaction_content)
        await self.session.commit()

    async def get_mentor_context(self, user_id: str) -> dict:
        """
        Retrieves all relevant memory pieces to prime the LLM prompt.
        """
        user = await self.user_repo.get_or_create_user(user_id)
        
        # Load relationships (simplified for SQLite)
        # Note: In production, we'd use joinedload or selectinload
        memories = await self.memory_repo.get_relevant_memories(user_id)
        
        # user.preferences is a scalar relationship (Mapped["UserPreference"])
        pref = user.preferences
        
        return {
            "preferences": {
                "level": pref.coding_level if pref else "beginner",
                "mentor_style": pref.mentor_style if pref else "socratic"
            },
            "recent_memories": [m.content for m in memories],
            "weaknesses": [w.topic for w in user.weaknesses]
        }

    async def track_weakness(self, user_id: str, topic: str, description: str, score: float = 0.5):
        """Tracks an identified coding gap for targeted mentoring."""
        await self.user_repo.add_weakness(user_id, topic, description, score)
        await self.session.commit()
