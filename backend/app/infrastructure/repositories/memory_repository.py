from typing import List, Optional, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload, joinedload
from app.domain.models import Memory, User, UserPreference, CodingWeakness
from datetime import datetime, UTC
import hashlib

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession):
        self.session = session

class MemoryRepository(BaseRepository[Memory]):
    async def add_memory(self, user_id: str, content: str, utility_score: float = 1.0) -> Memory:
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        stmt = select(Memory).where(Memory.user_id == user_id, Memory.content_hash == content_hash)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.last_accessed = datetime.now(UTC)
            existing.utility_score = min(existing.utility_score + 0.1, 5.0)
            return existing
            
        new_memory = Memory(
            user_id=user_id,
            content=content,
            content_hash=content_hash,
            utility_score=utility_score
        )
        self.session.add(new_memory)
        return new_memory

    async def get_relevant_memories(self, user_id: str, limit: int = 5) -> List[Memory]:
        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.utility_score.desc(), Memory.last_accessed.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

class UserRepository(BaseRepository[User]):
    async def get_or_create_user(self, user_id: str) -> User:
        """
        Fetches or creates a user. 
        Uses explicit loading to prevent MissingGreenlet errors.
        """
        # CRITICAL FIX: Use joinedload for 1-to-1 preferences to avoid async I/O crashes
        stmt = (
            select(User)
            .options(
                joinedload(User.preferences), 
                selectinload(User.weaknesses)
            )
            .where(User.id == user_id)
        )
        
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(id=user_id)
            self.session.add(user)
            
            pref = UserPreference(
                user_id=user_id, 
                coding_level="beginner", 
                mentor_style="socratic", 
                preferred_languages=[]
            )
            self.session.add(pref)
            
            await self.session.flush()
            
            # Refresh user with all relations loaded
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            
        return user

    async def update_preferences(self, user_id: str, **kwargs):
        stmt = update(UserPreference).where(UserPreference.user_id == user_id).values(**kwargs)
        await self.session.execute(stmt)

    async def add_weakness(self, user_id: str, topic: str, description: str, score: float):
        weakness = CodingWeakness(
            user_id=user_id,
            topic=topic,
            description=description,
            severity_score=score
        )
        self.session.add(weakness)
        return weakness
