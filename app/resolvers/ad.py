from functools import wraps

from gql import mutate, query

from app.db.models import Ad, Advertiser


@query('ads')
async def list_ads(parent, info):
    return await Ad.objects.all()


@query('advertisers')
async def list_advertisers(parent, info):
    return await Advertiser.objects.all()


def return_true(func):
    @wraps(func)
    async def wrap(*args, **kwargs):
        await func(*args, **kwargs)
        return True

    return wrap


@mutate
@return_true
async def create_advertiser(parent, info, name, file):
    await Advertiser.objects.create(dict(name=name, file=file))


@mutate
@return_true
async def update_advertiser(parent, info, id, **kwargs):
    if not kwargs:
        return

    await Advertiser.objects.filter_by(id=int(id)).update(kwargs)


@mutate
@return_true
async def delete_advertisers(parent, info, ids):
    if not ids:
        return

    await Advertiser.objects.filter(Advertiser.id.in_(map(int, ids))).delete()


@mutate
@return_true
async def create_ad(parent, info, name, file):
    await Ad.objects.create(dict(name=name, file=file))


@mutate
@return_true
async def update_ad(parent, info, id, **kwargs):
    if not kwargs:
        return

    await Ad.objects.filter_by(id=int(id)).update(kwargs)


@mutate
@return_true
async def delete_ads(parent, info, ids):
    if not ids:
        return

    await Ad.objects.filter(Advertiser.id.in_(map(int, ids))).delete()
