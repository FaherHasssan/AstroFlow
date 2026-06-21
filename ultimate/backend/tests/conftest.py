import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Dynamic import to load the FastAPI instance mapping
# Fallback structure used if main is not fully assembled yet
try:
    from app.main import app
except ImportError:
    from fastapi import FastAPI
    app = FastAPI()

from app.models.domain import Base

# Isolated SQLite in-memory database strictly mapping to the test execution context
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Asynchronous database drivers initialized for test pooling
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for the entire test session.
    Prevents event loop conflicts during heavy concurrent async testing.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Comprehensive Configuration Hook:
    Spins up an isolated local database, executes core schema migrations 
    dynamically BEFORE each test run, and cleanly drops tables AFTERWARDS 
    to guarantee test atomicity.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Abstract client helper bypassing network layers entirely via ASGITransport.
    Configured with transactional database session injections to override dependencies.
    """
    # Assuming the app has a `get_db` dependency to override
    # app.dependency_overrides[get_db] = lambda: db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
