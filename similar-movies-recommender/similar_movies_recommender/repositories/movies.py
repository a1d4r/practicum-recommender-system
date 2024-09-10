from dataclasses import dataclass

from elasticsearch import Elasticsearch

from similar_movies_recommender.models.movie_recommendations import SimilarMovieRecommendation
from similar_movies_recommender.models.movies import Movie, MovieID
from similar_movies_recommender.settings import settings


@dataclass
class MoviesRepository:
    client: Elasticsearch

    def fetch_movies(self, from_id: MovieID | None = None, size: int = 100) -> list[Movie]:
        result = self.client.search(
            index=settings.movies_index,
            search_after=[str(from_id)] if from_id is not None else None,
            size=size,
            query={"match_all": {}},
            sort={"id": {"order": "asc"}},
        )
        return [Movie.model_validate(hit["_source"]) for hit in result["hits"]["hits"]]

    def search_similar_movies(
        self, movie_id: MovieID, size: int = 10
    ) -> list[SimilarMovieRecommendation]:
        result = self.client.search(
            index=settings.movies_index,
            query={
                "more_like_this": {
                    "fields": [
                        "title",
                        "description",
                        "genres.name",
                        "actors.name",
                        "directors.name",
                    ],
                    "like": [{"_index": "movies", "_id": str(movie_id)}],
                    "min_term_freq": 1,
                    "max_query_terms": 12,
                }
            },
            size=size,
        )
        return [
            SimilarMovieRecommendation(
                movie_id=movie_id, similar_movie_id=hit["_id"], score=hit["_score"]
            )
            for hit in result["hits"]["hits"]
        ]
