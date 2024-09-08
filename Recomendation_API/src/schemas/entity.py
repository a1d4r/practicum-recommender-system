from uuid import UUID

from pydantic import BaseModel


class RecommendInDB(BaseModel):
    id: UUID
    user_id: UUID
    movie_id: UUID
    score: float


class SimilarMoviesInDB(BaseModel):
    id: UUID
    movie_id: UUID
    similar_movie_id: UUID
    score: float
