from pydantic import BaseModel

from similar_movies_recommender.models.movies import MovieID


class SimilarMovieRecommendation(BaseModel):
    movie_id: MovieID
    similar_movie_id: str
    score: float
