import asyncio
from abc import ABC, abstractmethod

import pandas as pd
from dotenv import load_dotenv

from surprise import SVD, accuracy
from surprise import Dataset, Reader
from surprise.model_selection import train_test_split

from schemas.md_entities import Like, HistoryWatching

load_dotenv()


class RecommendService(ABC):

    def __init__(self):
        self.model = SVD()
        self.ratings_df = None

    @abstractmethod
    async def load_data(self) -> None:
        pass

    @abstractmethod
    async def train_model(self) -> list:
        pass

    @abstractmethod
    async def get_user_recommendations(self, user_id: int, n_recommendations: int = 5) -> list:
        pass

    async def get_all_recommendations(self) -> list[list]:
        pass


class CollaborativeFilter(RecommendService):
    async def load_data(self) -> None:
        """Загрузка данных из MongoDB."""
        likes_data: list[Like] = await Like.find_all().to_list()
        likes_df = pd.DataFrame([{
            'user_id': str(like.user_id),
            'movie_id': str(like.movie_id),
            'rating': like.rating
        } for like in likes_data])

        history_data: list[HistoryWatching] = await HistoryWatching.find_all().to_list()

        history_df = pd.DataFrame([{
            'user_id': str(history.user_id),
            'movie_id': str(history.movie_id),
            'rating': 5
        } for history in history_data])

        self.ratings_df = pd.concat([likes_df, history_df]).drop_duplicates(
            subset=['user_id', 'movie_id'], keep='first')

    async def train_model(self) -> list:
        if self.ratings_df is None or self.ratings_df.empty:
            raise ValueError("DataFrame is empty or not loaded")

        required_columns = {'user_id', 'movie_id', 'rating'}
        if not required_columns.issubset(self.ratings_df.columns):
            raise KeyError(f"DataFrame does not contain necessary columns: {required_columns}")

        reader = Reader(rating_scale=(1, 10))
        input_data = Dataset.load_from_df(self.ratings_df[['user_id', 'movie_id', 'rating']], reader)
        trainset, testset = train_test_split(input_data, test_size=0.25)

        self.model.fit(trainset)

        predictions = self.model.test(testset)
        accuracy.rmse(predictions)
        return predictions

    async def get_user_recommendations(self, user_id: str, n_recommendations: int = 5) -> list:
        all_movie_ids = self.ratings_df['movie_id'].unique()
        rated_movies = self.ratings_df[self.ratings_df['user_id'] == user_id]['movie_id'].values
        movies_to_predict = [movie for movie in all_movie_ids if movie not in rated_movies]

        predictions = [self.model.predict(user_id, movie) for movie in movies_to_predict]
        predictions.sort(key=lambda x: x.est, reverse=True)

        top_n_recommendations = predictions[:n_recommendations]
        return [(user_id, pred.iid, pred.est) for pred in top_n_recommendations]

    async def get_all_recommendations(self) -> list[list]:
        all_users = self.ratings_df['user_id'].unique()
        tasks = [self.get_user_recommendations(user, n_recommendations=10) for user in all_users]
        result = await asyncio.gather(*tasks)
        return list(result)
