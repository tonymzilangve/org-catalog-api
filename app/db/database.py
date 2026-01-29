from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.core.config import settings


if settings.DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
else:
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}" \
        f"@{settings.POSTGRES_SERVER}/{settings.POSTGRES_DB}"
    )

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False    
)

Base = declarative_base()

async def get_db():
    async with async_session_maker() as session:
        yield session
