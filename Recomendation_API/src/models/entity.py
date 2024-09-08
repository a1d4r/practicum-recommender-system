from datetime import datetime
import uuid

from sqlalchemy import Column, Numeric, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()
SCHEMA = "recommendations"


class SchemaBase(Base):
    __abstract__ = True
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserRecommendation(SchemaBase):
    __tablename__ = 'user_recommendation'
    __table_args__ = {"schema": SCHEMA}

    user_id = Column(UUID(as_uuid=True), nullable=False)
    movie_id = Column(UUID(as_uuid=True), nullable=False)
    score = Column(Float, nullable=False)

    def __repr__(self):
        return f'<User_Recommendation: {self.user_id}:{self.movie_id}>'


class SimilarMovies(SchemaBase):
    __tablename__ = 'similar_movies'
    __table_args__ = {"schema": SCHEMA}

    movie_id = Column(UUID(as_uuid=True), nullable=False)
    similar_movie_id = Column(UUID(as_uuid=True), nullable=False)
    score = Column(Float, nullable=False)

    def __repr__(self):
        return f'<Similar_Movies: {self.movie_id}:{self.similar_movie_id}>'
