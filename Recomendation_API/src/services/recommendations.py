import uuid
from abc import ABC, abstractmethod
from typing import Sequence, Type

from fastapi import Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from db.postgres_db import get_pg_session
from db.redis_db import get_redis_service, CacheService
from models.entity import UserRecommendation, SimilarMovies, Base
from schemas.entity import RecommendInDB


class RecommendationServiceBase(ABC):

    def __init__(self, database_session: AsyncSession):
        self._db: AsyncSession = database_session
        self._cache_service: CacheService = get_redis_service(
            data_model=RecommendInDB,
            main_data_model=None
        )

    @abstractmethod
    async def get_recommendations(self, user_id: uuid.UUID) -> Sequence[UserRecommendation]:
        pass

    @abstractmethod
    async def get_similar_movies(self, movie_id: uuid.UUID) -> Sequence[UserRecommendation]:
        pass

    async def _get_data(self, key_prefix: str, item_id: uuid.UUID, model: Type[Base]) -> Sequence[Base]:
        cache_key = f'{key_prefix}_{item_id}'
        cache_result = await self._cache_service.get_from_cache(cache_key, key_prefix)
        if cache_result:
            return cache_result

        filter_field = 'user_id' if model is UserRecommendation else 'movie_id' if model is SimilarMovies else None

        if filter_field is None:
            raise ValueError(f"Unknown model: {model}")

        result = await self._db.execute(select(model).where(getattr(model, filter_field) == item_id))

        found_data = result.scalars().all()

        if not found_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        await self._cache_service.put_to_cache(found_data, cache_key, key_prefix)

        return found_data


class RecommendationService(RecommendationServiceBase):

    async def get_recommendations(self, user_id: uuid.UUID) -> Sequence[UserRecommendation]:
        return await self._get_data('user-recomm', user_id, UserRecommendation)

    async def get_similar_movies(self, movie_id: uuid.UUID) -> Sequence[SimilarMovies]:
        return await self._get_data('similar-movies', movie_id, SimilarMovies)


def get_recommendation_service(
        database_session: AsyncSession = Depends(get_pg_session),
) -> RecommendationService:
    return RecommendationService(
        database_session=database_session,
    )
