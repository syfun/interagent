from typing import NewType, Optional

from pydantic import BaseModel

ID = NewType('ID', int)


class Advertiser(BaseModel):
    id: Optional[ID]
    name: Optional[str]
    file: Optional[str]


class Ad(BaseModel):
    id: Optional[ID]
    file: Optional[str]
