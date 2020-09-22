from app.resolvers.ad import get_two_ads, meet_every_day
from app.types import Ad
from datetime import datetime


ads = [
    Ad(id=0),
    Ad(id=1, schedule=dict(type='every_day')),
    Ad(id=2, schedule=dict(type='every_day', start='12:00:00', end='19:00:00')),
    Ad(id=3, schedule=dict(type='every_day', start='00:00:00', end='12:00:00')),
    Ad(id=4, schedule=dict(type='weekday', weekday=2)),
    Ad(id=5, schedule=dict(type='weekday', weekday=7)),
    Ad(id=6, schedule=dict(type='date', date='2020-06-23')),
    Ad(id=7, schedule=dict(type='date', date='2020-06-24')),
]


def test_get_two_ads():
    now = datetime.strptime('2020-06-23 13:00:00', '%Y-%m-%d %H:%M:%S')
    data = get_two_ads(ads, now)
    assert len(data) == 2


def test_meet_every_day():
    assert meet_every_day('03:00:00', '04:00:00', '03:00:00')
    assert meet_every_day('03:00:00', '04:00:00', '03:20:00')
    assert meet_every_day('03:00:00', '04:00:00', '04:00:00')
    assert not meet_every_day('03:00:00', '04:00:00', '04:01:00')

    assert meet_every_day('16:00:00', '06:00:00', '16:00:00')
    assert meet_every_day('16:00:00', '06:00:00', '17:00:00')
    assert meet_every_day('16:00:00', '06:00:00', '06:00:00')
    assert meet_every_day('16:00:00', '06:00:00', '05:00:00')
