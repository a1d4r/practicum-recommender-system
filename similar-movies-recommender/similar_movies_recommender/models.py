from typing import NewType

from uuid import UUID

from pydantic import BaseModel

GenreID = NewType("GenreID", UUID)
PersonID = NewType("PersonID", UUID)
FilmID = NewType("FilmID", UUID)


class PersonIdName(BaseModel):
    """Модель для хранения идентификатора и имени актёра."""

    id: PersonID
    name: str


class GenreIdName(BaseModel):
    """Модель для хранения идентификатора и имени жанра."""

    id: GenreID
    name: str


class Film(BaseModel):
    """Модель для хранения информации о фильме."""

    id: FilmID
    title: str
    imdb_rating: float | None
    description: str | None
    genres: list[GenreIdName]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    actors: list[PersonIdName]
    writers: list[PersonIdName]
    directors: list[PersonIdName]
