import json

import pandas as pd
from sqlalchemy import delete
from async_fastapi_jwt_auth import AuthJWT

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from tests.functional.settings import get_settings
from tests.functional.models.auth import User
from tests.functional.models.entity import Base, UserRecommendation, SimilarMovies

settings = get_settings()

dsn = f'postgresql+asyncpg://{settings.ps_user}:{settings.ps_password}@{settings.ps_host}:{settings.ps_port}/{settings.ps_db}'

engine: AsyncEngine = create_async_engine(dsn, echo=False, future=True)

async_session: sessionmaker[AsyncSession] = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

if settings.debug:
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    async def purge_pg_database() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


async def insert_in_db(table_name: str):
    """Вставка тестовых данных в бд"""
    async with async_session() as session:
        match table_name:
            case 'user-recomm':
                df = pd.read_csv('/app/tests/functional/testdata/user_recomm.csv')
                for index, row in df.iterrows():
                    record = UserRecommendation(
                        user_id=row['user_id'],
                        movie_id=row['movie_id'],
                        score=row['score']
                    )
                    session.add(record)

            case 'similar-movies':
                df = pd.read_csv('/app/tests/functional/testdata/similar_movies.csv')
                for index, row in df.iterrows():
                    record = SimilarMovies(
                        movie_id=row['movie_id'],
                        similar_movie_id=row['similar_movie_id'],
                        score=row['score']
                    )
                    session.add(record)

            case _:
                raise ValueError(f"Unknown table: {table_name}")

        await session.commit()


async def delete_records(table: Base):
    """Удаление тестовых данных из бд"""
    async with async_session() as session:
        match table:
            case 'user-recomm':
                await session.execute(delete(UserRecommendation))
            case 'similar-movies':
                await session.execute(delete(SimilarMovies))
            case _:
                raise ValueError(f"Unknown table: {table}")
        await session.commit()


async def get_access_token(user: User = None) -> dict:
    authorize: AuthJWT = AuthJWT()
    if user:
        user_id = user.id
        roles = user.get_role_names()
    else:
        user_id = 'test'
        roles = ['superuser']
    access_subject = json.dumps({
        'user_id': str(user_id),
        'roles': roles
    })
    access_token = await authorize.create_access_token(subject=access_subject, algorithm='HS256')
    access_token_row = await authorize.get_raw_jwt(encoded_token=access_token)
    return {'access_token': access_token, 'access_token_row': access_token_row}


async def get_pg_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
