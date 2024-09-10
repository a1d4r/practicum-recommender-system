from dataclasses import dataclass

import psycopg

from psycopg.rows import DictRow

from similar_movies_recommender.models.movie_recommendations import SimilarMovieRecommendation


@dataclass
class MovieRecommendationsRepository:
    connection: psycopg.Connection[DictRow]

    def add_recommendations(self, recommendations: list[SimilarMovieRecommendation]) -> None:
        with self.connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO similar_movies (movie_id, similar_movie_id, score) VALUES (%s, %s, %s) "
                "ON CONFLICT (movie_id, similar_movie_id) DO UPDATE SET score = excluded.score",
                [
                    (recommendation.movie_id, recommendation.similar_movie_id, recommendation.score)
                    for recommendation in recommendations
                ],
            )
        self.connection.commit()
