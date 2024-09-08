import asyncio

from beanie import init_beanie

import config
from schemas.md_entities import Like, HistoryWatching

from motor.motor_asyncio import AsyncIOMotorClient

from services.recommender import schedule_recommendations

settings = config.get_settings()


async def setup():
    client = AsyncIOMotorClient(settings.mongodb_uri)
    await init_beanie(
        database=client.get_database(settings.db_name),
        document_models=[Like, HistoryWatching],
        allow_index_dropping=True
    )


async def main():
    await setup()
    await schedule_recommendations()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
