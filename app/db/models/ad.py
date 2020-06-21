from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from app import types
from app.db.base_class import Base


class Advertiser(Base):
    __tablename__ = 'advertisers'
    __schema__ = types.Advertiser

    name = Column(String, nullable=False)
    file = Column(String, nullable=True)


# Ad schedule
# {"type": "every_day", "start": "", "end": ""}
# {"type": "weekday", "weekday": ""}
# {"type": "date", "date": ""}
class Ad(Base):
    __tablename__ = 'ads'
    __schema__ = types.Ad

    file = Column(String, nullable=False)
    schedule = Column(JSONB, nullable=True)

    def to_dict(self):
        return dict(id=self.id, file=self.file, schedule=self.schedule)
