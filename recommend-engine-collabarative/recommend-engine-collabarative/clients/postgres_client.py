from contextlib import asynccontextmanager

import config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from schemas.pg_entities import Base

settings = config.get_settings()

dsn = (
    f"postgresql+asyncpg://"
    f"{settings.pg_db_user}:{settings.pg_db_pass}@{settings.pg_db_host}:"
    f"{settings.pg_db_port}/{settings.pg_db_name}"
)

engine: AsyncEngine = create_async_engine(dsn, echo=False, future=True)

async_session: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

if settings.debug:

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def purge_pg_database() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@asynccontextmanager
async def get_pg_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
