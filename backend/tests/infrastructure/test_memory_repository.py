import pytest
from app.infrastructure.repositories.memory_repository import MemoryRepository, UserRepository
from app.domain.models import User, Memory

@pytest.mark.asyncio
async def test_add_memory_duplicate_prevention(db_session):
    repo = MemoryRepository(db_session)
    user_id = "test_user_1"
    content = "Hello, I am learning Python."
    
    # Add first time
    mem1 = await repo.add_memory(user_id, content)
    await db_session.commit()
    
    # Add second time (exact same content)
    mem2 = await repo.add_memory(user_id, content)
    await db_session.commit()
    
    assert mem1.id == mem2.id
    assert mem2.utility_score > 1.0  # Verify score incremented

@pytest.mark.asyncio
async def test_get_or_create_user(db_session):
    repo = UserRepository(db_session)
    user_id = "new_user_123"
    
    user = await repo.get_or_create_user(user_id)
    assert user.id == user_id
    assert user.preferences is not None
    assert user.preferences.coding_level == "beginner"
