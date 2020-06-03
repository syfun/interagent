from app.db.models import Ad, Advertiser
from .resolver import ResolverSet


class AdvertiserResolverSet(ResolverSet):
    model = Advertiser
    resource = 'Advertiser'


class AdResolverSet(ResolverSet):
    model = Ad
    resource = 'Ad'
