from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.dialects.postgresql import insert
from schemas.pg_entities import UserRecommendation

import config

settings = config.get_settings()

dsn = (
    f"postgresql+asyncpg://"
    f"{settings.pg_db_user}:{settings.pg_db_pass}@{settings.pg_db_host}:"
    f"{settings.pg_db_port}/{settings.pg_db_name}"
)

engine: AsyncEngine = create_async_engine(dsn, echo=False, future=True)

async_session: sessionmaker[AsyncSession] = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def add_recommendations(recommendations: list[UserRecommendation]) -> None:
    async with async_session() as session:
        try:
            async with session.begin():
                for recommendation in recommendations:
                    stmt = insert(UserRecommendation).values(
                        user_id=recommendation.user_id,
                        movie_id=recommendation.movie_id,
                        score=recommendation.score
                    ).on_conflict_do_update(
                        index_elements=['user_id', 'movie_id'],
                        set_={'score': recommendation.score}
                    )
                    await session.execute(stmt)

            await session.commit()
        except Exception:
            await session.rollback()
            raise
