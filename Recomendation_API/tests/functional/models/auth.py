import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey, Table, Text, UniqueConstraint, or_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base, backref
from werkzeug.security import check_password_hash, generate_password_hash


Base = declarative_base()
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE")),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete="CASCADE"))
)


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    roles = relationship('Role', secondary=user_role,  cascade="all,delete", back_populates='users')

    def __init__(self, login: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def get_user_by_universal_login(cls, login: str | None, email: str | None):
        return cls.query.filter(or_(cls.login == login, cls.email == email)).first()

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def get_role_names(self):
        return [role.name for role in self.roles]

    def to_dict(self):
        user_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        user_dict['roles'] = [role.name for role in self.roles]
        return user_dict

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    users = relationship('User', secondary=user_role,  cascade="all,delete", back_populates='roles')

    def __init__(self, name: str, _id: uuid.UUID = None) -> None:
        self.name = name
        if _id is not None:
            self.id = _id

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f'{self.name}'