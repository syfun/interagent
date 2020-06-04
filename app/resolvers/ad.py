from gql import query

from app.db.models import Ad, Advertiser


@query('ads')
async def list_ads(parent, info):
    return await Ad.objects.all()


@query('advertisers')
async def list_advertisers(parent, info):
    return await Advertiser.objects.all()
