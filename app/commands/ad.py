import asyncio
from functools import wraps

from app.db import database as db
from app.db.models import Ad
from app import types


def db_init(func):
    @wraps(func)
    async def wrap(*args, **kwargs):
        await db.connect()

        try:
            return await func(*args, **kwargs)
        finally:
            await db.disconnect()

    return wrap


@db_init
async def add_ads():
    ads = [
        types.Ad(file='1', schedule=dict(type='every_day', start='12:00:00', end='19:00:00')),
        types.Ad(file='2', schedule=dict(type='every_day', start='00:00:00', end='12:00:00')),
        types.Ad(file='3', schedule=dict(type='weekday', weekday=2)),
        types.Ad(file='4', schedule=dict(type='weekday', weekday=7)),
        types.Ad(file='5', schedule=dict(type='date', date='2020-06-21')),
        types.Ad(file='6', schedule=dict(type='date', date='2020-06-24')),
    ]
    await Ad.objects.create_many(ads)


if __name__ == '__main__':
    asyncio.run(add_ads())
