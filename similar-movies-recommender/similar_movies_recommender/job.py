from similar_movies_recommender.dependencies import get_recommendation_engine


def calculate_movie_recommendations() -> None:
    with get_recommendation_engine() as recommendation_engine:
        recommendation_engine.calculate_movies_recommendations()


if __name__ == "__main__":
    calculate_movie_recommendations()
