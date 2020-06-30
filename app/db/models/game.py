from sqlalchemy import Column, String, DateTime, Integer

from app import types
from app.db.base_class import Base


class GameSession(Base):
    __tablename__ = 'game_sessions'
    __schema__ = types.GameSession

    user_id = Column(String, nullable=False)
    avatar = Column(String, nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)
