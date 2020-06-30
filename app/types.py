from datetime import datetime
from typing import NewType, Optional

from pydantic import BaseModel, Field

ID = NewType('ID', int)


class Advertiser(BaseModel):
    id: Optional[ID]
    name: Optional[str]
    file: Optional[str]


class Ad(BaseModel):
    id: Optional[ID]
    file: Optional[str]
    schedule: Optional[dict]


class Ranking(BaseModel):
    ranking: Optional[ID]
    user_id: Optional[str]
    avatar: Optional[str]
    score: Optional[int]


class StartGameInput(BaseModel):
    user_id: str
    avatar: str
    start_at: datetime = Field(default_factory=datetime.now)


class EndGameInput(BaseModel):
    score: int
    end_at: datetime = Field(default_factory=datetime.now)


class GameSession(BaseModel):
    id: Optional[int]
    user_id: Optional[str]
    avatar: Optional[str]
    score: Optional[int]
    start_at: Optional[datetime]
    end_at: Optional[datetime]
