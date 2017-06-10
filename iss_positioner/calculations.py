# -*- coding: utf-8  -*-
import asyncio
import math
from collections import OrderedDict
from datetime import datetime, date, timedelta

from ephem import readtle

from .util import datetime_range, find_le

__all__ = (
    'AsyncSatellite',
    'Satellite',
    'TLENotFound',
)


class TLENotFound(ValueError):
    pass


class Satellite(object):
    _tle_db = None

    def __init__(self, *, tles=None):
        self.tle_db = tles

    @property
    def tle_db(self):
        return self._tle_db

    @tle_db.setter
    def tle_db(self, values):
        self._tle_db = OrderedDict((self.tle_date(tle), tle) for tle in values or [])

    def get_nearest_tle(self, dt=None, ignore=True):
        return self.tle_db[self.get_nearest_tle_dt(dt, ignore)]

    def get_nearest_tle_dt(self, dt=None, ignore=True):
        tle_dts = tuple(self.tle_db.keys())

        if not isinstance(dt, (datetime, date)):
            return tle_dts[0]

        try:
            tle_dt = find_le(tle_dts, dt)
        except ValueError:
            if ignore:
                return tle_dts[0]
            raise TLENotFound('Not found TLE for %r, the oldest TLE in db for %r' % (dt, tle_dts[0]))
        else:
            return tle_dt

    @staticmethod
    def tle_date(tle):
        fmt = '%Y-%m-%d %H:%M:%S.%f'
        return datetime.strptime('{epoch}.{epoch_microseconds}'.format(**tle), fmt)

    def get(self, dt, *, tle=None):
        if tle is None and isinstance(dt, (datetime, date)):
            tle = self.get_nearest_tle(dt)
        return readtle(tle['tle_line0'], tle['tle_line1'], tle['tle_line2'])

    def get_position(self, dt, *, tle=None):
        iss = self.get(dt, tle=tle)
        iss.compute(dt)
        return math.degrees(iss.sublong), math.degrees(iss.sublat), dt.isoformat(' ')


class AsyncSatellite(Satellite):
    _loop = None

    def __init__(self, *, tles=None, loop=None):
        super().__init__(tles=tles)
        if loop is None:
            loop = asyncio.get_event_loop()

        self._loop = loop

    @property
    def loop(self):
        return self._loop

    async def get_position(self, dt, *, tle=None):
        return super().get_position(dt, tle=tle)

    async def compute(self, start_dt=None, end_dt=None, step=1):
        if not isinstance(start_dt, datetime):
            start_dt = datetime.utcnow()
        if not isinstance(end_dt, datetime):
            end_dt = start_dt + timedelta(days=1)
        fs = (self.get_position(t) for t in datetime_range(start_dt, end_dt, step))
        return await asyncio.gather(*fs, loop=self.loop)
