import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from clients.postgres_client import get_pg_session
from clients.svd_client import CollaborativeFilter
from schemas.pg_entities import UserRecommendation

settings = config.get_settings()


async def build_and_store_recommendations():
    recommend_data = CollaborativeFilter()
    await recommend_data.load_data()

    recommend_data.train_model()

    async with get_pg_session() as session:
        all_users = recommend_data.ratings_df['user_id'].unique()
        for user_id in all_users:
            user_recommendations = recommend_data.get_user_recommendations(user_id=user_id, n_recommendations=10)

            for movie_id, score in user_recommendations:
                recommendation = UserRecommendation(
                    user_id=user_id,
                    movie_id=movie_id,
                    score=score
                )
                await session.merge(recommendation)

        await session.commit()


async def schedule_recommendations():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(build_and_store_recommendations, 'cron', hour=0, minute=0)
    scheduler.start()
