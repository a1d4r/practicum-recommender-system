import uuid
from typing import Sequence, Annotated

from fastapi import APIRouter, Depends, status

from core import config
from models.entity import UserRecommendation
from schemas.entity import RecommendInDB, SimilarMoviesInDB
from services.auth import security_jwt
from services.recommendations import RecommendationService, get_recommendation_service

settings = config.get_settings()

router = APIRouter()


@router.get(
    '/user-recommendations/{user_id}',
    response_model=Sequence[RecommendInDB],
    status_code=status.HTTP_200_OK
)
async def user_recommend(
        # user: Annotated[dict, Depends(security_jwt(required_roles=[]))],
        user_id: uuid.UUID,
        recommendation_service: RecommendationService = Depends(get_recommendation_service),
        ) -> Sequence[UserRecommendation]:
    return await recommendation_service.get_recommendations(user_id)


@router.get(
    '/similar-movies/{movie_id}',
    response_model=Sequence[SimilarMoviesInDB],
    status_code=status.HTTP_200_OK
)
async def similar_movies(
        # user: Annotated[dict, Depends(security_jwt(required_roles=[]))],
        movie_id: uuid.UUID,
        recommendation_service: RecommendationService = Depends(get_recommendation_service),
        ) -> Sequence[SimilarMoviesInDB]:
    return await recommendation_service.get_similar_movies(movie_id)
