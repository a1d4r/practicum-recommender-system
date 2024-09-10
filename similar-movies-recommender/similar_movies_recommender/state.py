from typing import Generic, TypeVar

import threading

from collections.abc import Iterator
from contextlib import contextmanager

from loguru import logger
from pydantic import BaseModel, ValidationError

from similar_movies_recommender.models.movies import MovieID
from similar_movies_recommender.storage.base import BaseStorage

T = TypeVar("T", bound=BaseModel)


class State(BaseModel):
    """Состояние рекомендательного движка."""

    last_movie_id: MovieID | None = None


class StateManager(Generic[T]):
    _lock = threading.Lock()  # shared lock among all threads

    def __init__(self, storage: BaseStorage, state_class: type[T], default_state: T) -> None:
        self.storage = storage
        self.state_class = state_class
        self.default_state = default_state

    def _get_state(self) -> T:
        """Получить состояние из хранилища."""
        try:
            return self.state_class.model_validate(self.storage.retrieve_state())
        except ValidationError:
            logger.warning(
                "State data is invalid. Falling back to default state: {}", self.default_state
            )
            return self.default_state.model_copy()

    @contextmanager
    def acquire_state(self) -> Iterator[T]:
        """Получить состояние и заблокировать его для других потоков на время использования."""
        logger.debug("Acquiring state lock...")
        with self._lock:
            logger.debug("State lock acquired")
            yield self._get_state()
            logger.debug("State lock released")

    def save_state(self, state: T) -> None:
        """Сохранить состояние в хранилище."""
        if not self._lock.locked():
            logger.warning(
                "Trying to save state without acquiring lock. State changes will be lost."
            )
            return
        self.storage.save_state(state.model_dump(mode="json"))
