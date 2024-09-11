from datetime import datetime

from clients.postgres_client import add_recommendations
from clients.svd_client import CollaborativeFilter
from schemas.pg_entities import UserRecommendation
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config

settings = config.get_settings()


async def build_and_store_recommendations():
    collaborative_filter = CollaborativeFilter()

    await collaborative_filter.load_data()
    await collaborative_filter.train_model()

    recommendations = await collaborative_filter.get_all_recommendations()
    flat_recommendations = [user_recommendation for sublist in recommendations for user_recommendation in sublist]

    user_recommendation_objects = [
        UserRecommendation(user_id=user_id, movie_id=movie_id, score=est)
        for user_id, movie_id, est in flat_recommendations
    ]

    await add_recommendations(recommendations=user_recommendation_objects)


async def schedule_recommendations():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(build_and_store_recommendations, 'cron', hour=0, minute=0, next_run_time=datetime.now())
    scheduler.start()
