import logging
from functools import wraps
from datetime import datetime
from random import randint
from urllib.parse import urljoin, quote_plus

from gql import mutate, query, field_resolver

from app.db.models import Ad, Advertiser
from app import types, settings

# Ad schedule
# {"type": "every_day", "start": "", "end": ""}
# {"type": "weekday", "weekday": ""}
# {"type": "date", "date": ""}
logger = logging.getLogger(__name__)


def meet_every_day(start, end, time):
    if end == '00:00:00':
        end = '24:00:00'

    if start <= time <= end:
        return True
    if start > end and (start <= time <= '24:00:00' or time <= end):
        return True
    return False


def get_two_ads(ads: types.Ad, now: datetime = None):
    now = now or datetime.now()
    weekday = now.isoweekday()
    date, time = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
    to_random = []
    default_ads = []
    for ad in ads:
        schedule = ad.schedule
        if not schedule:
            continue
        if ad.default:
            default_ads.append(ad)
            continue
        if (
            schedule["type"] == "every_day"
            and (start := schedule.get("start"))
            and (end := schedule.get("end"))
        ):
            if meet_every_day(start, end, time):
                to_random.append(ad)
        elif schedule["type"] == "weekday" and schedule.get("weekday") == weekday:
            to_random.append(ad)
        elif schedule["type"] == "date" and schedule.get("date") == date:
            to_random.append(ad)
    length = len(to_random)
    if not length:
        return [default_ads[randint(0, len(default_ads) - 1)]]
    if length == 1:
        return to_random
    data = to_random[randint(0, length - 1)]
    return [data]
    # data = sample(to_random, k=2)
    # if data[0].id > data[1].id:
    #     data = reversed(data)
    # return data


@field_resolver('Ad', 'file')
def get_ad_url(parent, info):
    return urljoin(settings.FILE_PREFIX, 'media/' + quote_plus(parent.file))


@query("ads")
async def list_ads(parent, info):
    ads = await Ad.objects.all()
    ads = get_two_ads(ads)
    return ads


@query("advertisers")
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
