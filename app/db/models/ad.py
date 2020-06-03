from sqlalchemy import Column, String

from app import types
from app.db.base_class import Base


class Advertiser(Base):
    __tablename__ = 'advertisers'
    __schema__ = types.Advertiser

    name = Column(String, nullable=False)
    file = Column(String, nullable=True)


class Ad(Base):
    __tablename__ = 'ads'
    __schema__ = types.Ad

    file = Column(String, nullable=False)
