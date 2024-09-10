from datetime import UTC, datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from similar_movies_recommender.dependencies import get_recommendation_engine
from similar_movies_recommender.settings import settings

scheduler = BlockingScheduler()


@scheduler.scheduled_job(
    "interval", seconds=settings.run_interval_seconds, next_run_time=datetime.now(UTC)
)
def calculate_movie_recommendations() -> None:
    with get_recommendation_engine() as recommendation_engine:
        recommendation_engine.calculate_movies_recommendations()
