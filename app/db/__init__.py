from functools import wraps

from databases import Database

from app import settings

if settings.TESTING:
    database = Database(settings.DATABASE_URL, force_rollback=True)
else:
    database = Database(settings.DATABASE_URL)


def transaction(func):
    @wraps(func)
    async def wrap(*args, **kwargs):
        tx = await database.transaction()
        try:
            res = await func(*args, **kwargs)
        except Exception as exc:
            await tx.rollback()
            raise exc
        else:
            await tx.commit()
            return res

    return wrap
