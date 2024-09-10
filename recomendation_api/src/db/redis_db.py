from abc import ABC, abstractmethod
from typing import Type, TypeVar
from uuid import UUID

import orjson
from pydantic import BaseModel
from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from core.config import get_settings
from db.backoff_decorator import backoff
from models.entity import UserRecommendation, SimilarMovies

settings = get_settings()

redis: Redis | None = None

DATA_CACHE_EXPIRE_IN_SECONDS = 60 * 5
T = TypeVar('T', bound=BaseModel)


def initialize_redis():
    global redis
    redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        decode_responses=True
    )


class CacheService(ABC):
    @abstractmethod
    async def get_from_cache(self, key_cache: str, table: str) -> T | list[T] | None:
        pass

    @abstractmethod
    async def put_to_cache(self, data, key_cache: str, table: str) -> None:
        pass


class RedisCacheService(CacheService):
    def __init__(self, data_model, main_data_model=None):
        self.redis: Redis | None = redis
        if not self.redis:
            initialize_redis()
            self.redis: Redis | None = redis

        self.data_model = data_model

        if main_data_model:
            self.main_data_model = main_data_model
        else:
            self.main_data_model = data_model

    @backoff((ConnectionError,), 1, 2, 100, 10)
    async def get_from_cache(self, key_cache: str, table: str) -> list:
        data = await self.redis.get(key_cache)
        if not data:
            return None

        recomm_list = []
        data_list = orjson.loads(data)

        match table:
            case 'user-recomm':
                for item in data_list:
                    recommendation = UserRecommendation(
                        id=UUID(item['id']),
                        user_id=UUID(item['user_id']),
                        movie_id=UUID(item['movie_id']),
                        score=item['score'],
                        created_at=item['created_at']
                    )
                    recomm_list.append(recommendation)
            case 'similar-movies':
                for item in data_list:
                    recommendation = SimilarMovies(
                        id=UUID(item['id']),
                        movie_id=UUID(item['movie_id']),
                        similar_movie_id=UUID(item['similar_movie_id']),
                        score=item['score'],
                        created_at=item['created_at']
                    )
                    recomm_list.append(recommendation)
            case _:
                raise ValueError(f"Unknown table: {table}")

        return recomm_list

    @backoff((ConnectionError,), 1, 2, 100, 10)
    async def put_to_cache(self, data, key_cache: str, table: str):

        if isinstance(data, list):
            recom_list = []

            match table:
                case 'user-recomm':
                    for index, item in enumerate(data):
                        recommendation_dict = {
                            'id': str(item.id),
                            'user_id': str(item.user_id),
                            'movie_id': str(item.movie_id),
                            'score': item.score,
                            'created_at': item.created_at
                        }
                        recom_list.append(recommendation_dict)
                case 'similar-movies':
                    for index, item in enumerate(data):
                        recommendation_dict = {
                            'id': str(item.id),
                            'movie_id': str(item.movie_id),
                            'similar_movie_id': str(item.similar_movie_id),
                            'score': item.score,
                            'created_at': item.created_at
                        }
                        recom_list.append(recommendation_dict)
                case _:
                    raise ValueError(f"Unknown table: {table}")

            await self.redis.set(key_cache, orjson.dumps(recom_list), DATA_CACHE_EXPIRE_IN_SECONDS)

        else:
            await self.redis.set(key_cache, data.json(), DATA_CACHE_EXPIRE_IN_SECONDS)


def get_redis_service(
        data_model: Type[BaseModel],
        main_data_model: Type[BaseModel] = None
):
    redis_service = RedisCacheService(
        data_model=data_model,
        main_data_model=main_data_model
    )
    return redis_service
