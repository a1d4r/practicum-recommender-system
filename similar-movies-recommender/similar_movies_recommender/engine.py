from dataclasses import dataclass

from loguru import logger

from similar_movies_recommender.repositories.movie_recommendations import (
    MovieRecommendationsRepository,
)
from similar_movies_recommender.repositories.movies import MoviesRepository
from similar_movies_recommender.state import State, StateManager


@dataclass
class RecommendationEngine:
    state_manager: StateManager[State]
    movies_repository: MoviesRepository
    movie_recommendations_repository: MovieRecommendationsRepository

    def calculate_movies_recommendations(self) -> None:
        with self.state_manager.acquire_state() as state:
            logger.info("Last movie id: {}", state.last_movie_id)
            recommendations = []
            for movie in self.movies_repository.fetch_movies(from_id=state.last_movie_id):
                similar_movies_recommendations = self.movies_repository.search_similar_movies(
                    movie.id
                )
                logger.debug(
                    "Calculated movie recommendations for movie {} ({}): {}",
                    movie.title,
                    movie.id,
                    [similar_movies_recommendations],
                )
                recommendations.extend(similar_movies_recommendations)
            if recommendations:
                self.movie_recommendations_repository.add_recommendations(recommendations)
                state.last_movie_id = recommendations[-1].movie_id
                self.state_manager.save_state(state)
            logger.info("Saved {} movie recommendations", len(recommendations))
