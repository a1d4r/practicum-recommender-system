from dataclasses import dataclass

from elasticsearch import Elasticsearch

from similar_movies_recommender.models import Film
from similar_movies_recommender.settings import settings


@dataclass
class MoviesRepository:
    client: Elasticsearch

    def fetch_movies(self, from_id: str | None = None, size: int = 100) -> list[Film]:
        result = self.client.search(
            index=settings.movies_index, search_after=from_id, size=size, query={"match_all": {}}
        )
        return [Film.model_validate(hit["_source"]) for hit in result["hits"]["hits"]]

    def search_similar_movies(self, movie_id: str, size: int = 10) -> list[Film]:
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
                    "like": [{"_index": "movies", "_id": movie_id}],
                    "min_term_freq": 1,
                    "max_query_terms": 12,
                }
            },
            size=size,
        )
        return [Film.model_validate(hit["_source"]) for hit in result["hits"]["hits"]]
