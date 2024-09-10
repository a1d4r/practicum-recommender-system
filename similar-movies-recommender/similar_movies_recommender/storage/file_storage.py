from typing import Any, cast

import json

from pathlib import Path

from loguru import logger

from similar_movies_recommender.storage.base import BaseStorage


class JsonFileStorage(BaseStorage):
    """Реализация хранилища, использующего локальный файл.

    Формат хранения: JSON
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def save_state(self, state: dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        with self.file_path.open("w") as file:
            logger.info("Saved state to {}", self.file_path)
            json.dump(state, file)

    def retrieve_state(self) -> dict[str, Any]:
        """Получить состояние из хранилища."""
        try:
            with self.file_path.open("r") as file:
                state = cast(dict[str, Any], json.load(file))
        except FileNotFoundError:
            logger.warning("State file {} not found. Falling back to empty state", self.file_path)
            state = {}
        else:
            logger.info("Retrieved state from {}", self.file_path)

        return state
