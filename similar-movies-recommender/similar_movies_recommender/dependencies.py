from collections.abc import Iterator
from contextlib import closing, contextmanager

import psycopg
import tenacity

from elasticsearch import Elasticsearch
from loguru import logger
from psycopg.rows import DictRow, dict_row

from similar_movies_recommender.engine import RecommendationEngine
from similar_movies_recommender.repositories.movie_recommendations import (
    MovieRecommendationsRepository,
)
from similar_movies_recommender.repositories.movies import MoviesRepository
from similar_movies_recommender.settings import settings
from similar_movies_recommender.state import State, StateManager
from similar_movies_recommender.storage.file_storage import JsonFileStorage


@contextmanager
def get_pg_connection() -> Iterator[psycopg.Connection[DictRow]]:
    for attempt in tenacity.Retrying(
        before_sleep=tenacity.before_sleep_log(logger, "ERROR"),  # type: ignore[arg-type]
        after=tenacity.after_log(logger, "INFO"),  # type: ignore[arg-type]
        retry=tenacity.retry_if_exception_type(psycopg.OperationalError),
        wait=settings.retry_policy,
    ):
        with (
            attempt,
            closing(psycopg.connect(str(settings.postgres_dsn), row_factory=dict_row)) as pg_conn,
        ):
            logger.debug("Connecting to PostgreSQL...")
            yield pg_conn


@contextmanager
def get_es_client() -> Iterator[Elasticsearch]:
    with closing(Elasticsearch(settings.elasticsearch_host)) as es_client:
        yield es_client


@contextmanager
def get_movies_repository() -> Iterator[MoviesRepository]:
    with get_es_client() as es_client:
        yield MoviesRepository(es_client)


@contextmanager
def get_movie_recommendations_repository() -> Iterator[MovieRecommendationsRepository]:
    with get_pg_connection() as pg_conn:
        yield MovieRecommendationsRepository(pg_conn)


def get_state_manager() -> StateManager[State]:
    storage = JsonFileStorage(settings.state_file_path)
    return StateManager(storage, State, State(last_movie_id=None))


@contextmanager
def get_recommendation_engine() -> Iterator[RecommendationEngine]:
    state_manager = get_state_manager()
    with (
        get_movies_repository() as movies_repository,
        get_movie_recommendations_repository() as movie_recommendations_repository,
    ):
        yield RecommendationEngine(
            state_manager, movies_repository, movie_recommendations_repository
        )
