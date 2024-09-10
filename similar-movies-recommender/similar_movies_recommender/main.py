import sys

from loguru import logger

from similar_movies_recommender.job import scheduler
from similar_movies_recommender.settings import settings

if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stdout, level=settings.log_level)
    scheduler.start()
