from abc import ABC, abstractmethod
import pickle
from datetime import datetime

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
    def train_model(self) -> list:
        pass

    @abstractmethod
    def get_user_recommendations(self, user_id: int, n_recommendations: int = 5) -> list:
        pass

    def get_all_recommendations(self):
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

    def train_model(self) -> list:
        reader = Reader(rating_scale=(1, 10))
        input_data = Dataset.load_from_df(self.ratings_df[['user_id', 'movie_id', 'rating']], reader)
        trainset, testset = train_test_split(input_data, test_size=0.25)

        self.model.fit(trainset)

        predictions = self.model.test(testset)
        accuracy.rmse(predictions)

        with open(f'svd_model-{datetime.now().strftime("%y-%m-%d_%H-%M-%S")}.pkl', 'wb') as f:
            pickle.dump(self.model, f)

        return predictions

    def load_model(self, date_file: str) -> bool:
        with open(date_file, 'rb') as f:
            self.model = pickle.load(f)
        return True

    def get_user_recommendations(self, user_id: str, n_recommendations: int = 5) -> list:
        all_movie_ids = self.ratings_df['movie_id'].unique()
        rated_movies = self.ratings_df[self.ratings_df['user_id'] == user_id]['movie_id'].values
        movies_to_predict = [movie for movie in all_movie_ids if movie not in rated_movies]

        predictions = [self.model.predict(user_id, movie) for movie in movies_to_predict]
        predictions.sort(key=lambda x: x.est, reverse=True)

        top_n_recommendations = predictions[:n_recommendations]
        return [(pred.iid, pred.est) for pred in top_n_recommendations]

    def get_all_recommendations(self) -> list[list]:
        result = []
        all_users = self.ratings_df['user_id'].unique()
        for user in all_users:
            user_recommend = self.get_user_recommendations(user, n_recommendations=10)
            result.append(user_recommend)
        return result
