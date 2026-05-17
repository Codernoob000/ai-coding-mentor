import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.infrastructure.database import Base, get_db
from unittest.mock import AsyncMock, MagicMock

# --- Database Fixtures ---
# Use a static URL for in-memory testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
async def test_engine():
    # FIX: Maintain a persistent connection for the session to prevent in-memory DB loss
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        # Rollback ensures tests remain isolated even on failure
        await session.rollback()

# --- API Fixtures ---
@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _get_test_db
    # CRITICAL FIX: Ensure overrides are ALWAYS cleared via finally block
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()

# --- Mocking Fixtures ---
@pytest.fixture
def mock_gemini_service():
    service = MagicMock()
    service.generate_response = AsyncMock(return_value="Mocked response")
    service.health_check = AsyncMock(return_value=True)
    return service

@pytest.fixture
def mock_mcp_service():
    service = MagicMock()
    service.get_tool_definitions = AsyncMock(return_value=[])
    service.execute_tool = AsyncMock(return_value="Mock tool result")
    return service
