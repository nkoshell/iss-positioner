# -*- coding: utf-8 -*-
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import chain

from .calculations import AsyncSatellite
from .log import tqdm
from .util import datetime_range, geo_member_to_dict

__all__ = (
    'fill_db',
    'clear_old_coords',
    'store_coords',
    'get_coords',
    'geo_radius',
)


async def clear_old_coords(redis, *, start_dt=None, end_dt=None, calculation_step=timedelta(hours=1)):
    today = datetime(*datetime.today().timetuple()[:3])
    if not end_dt:
        end_dt = today
    if not start_dt:
        start_dt = end_dt - timedelta(days=14)
    keys = (dt.isoformat(' ') for dt in datetime_range(start_dt, end_dt, calculation_step))
    deleted_count = await redis.delete(*keys)
    return deleted_count, start_dt, end_dt


async def fill_db(redis, satellite, tle_getter):
    if not callable(tle_getter):
        raise ValueError('Argument `tle_getter` must be callable object')

    satellite.tle_db = (tle['extra_info'] for tle in await tle_getter())
    return await store_coords(satellite, redis)


async def geo_radius(redis, *, dt, lon, lat, **params):
    vals = await redis.georadius(dt.isoformat(' '), lon, lat,
                                 params.get('dist', 250), unit=params.get('unit', 'km'),
                                 with_dist=True, with_coord=True, with_hash=True)
    vals.sort(key=lambda val: val.member)
    return [geo_member_to_dict(val, units=params.get('unit', 'km')) for val in vals]


async def get_coords(redis, *, start_dt, end_dt, step, calculation_step=timedelta(hours=1), loop=None):
    _start, _end = datetime(*start_dt.timetuple()[:4]), datetime(*end_dt.timetuple()[:4])

    dt_set = defaultdict(list)
    for dt in datetime_range(_start, _end, calculation_step):
        for t in datetime_range(dt, dt + calculation_step, step):
            if start_dt == end_dt and t == start_dt:
                dt_set[dt.isoformat(' ')].append(t.isoformat(' '))
                break

            if start_dt <= t < end_dt:
                dt_set[dt.isoformat(' ')].append(t.isoformat(' '))

    fs = (redis.geopos(k, *v) for k, v in dt_set.items())
    coords_set = await asyncio.gather(*fs, loop=loop)
    dt_set = zip(chain.from_iterable(dt_set.values()), chain.from_iterable(coords_set))
    return [dict(dt=dt, coords=coords._asdict()) for dt, coords in dt_set]


async def store_coords(satellite, redis, *, calculation_step=timedelta(hours=1), clear_old=True):
    if not isinstance(satellite, AsyncSatellite):
        raise ValueError('Argument `satellite` must be is instance `AsyncSatellite` class')

    dts = tuple(satellite.tle_db.keys())
    start_dt, end_dt = datetime(*datetime.today().timetuple()[:3]), dts[-1] + timedelta(days=14)
    added_count = 0
    for dt in tqdm(tuple(datetime_range(start_dt, end_dt, calculation_step)), mininterval=1):
        coords = await satellite.compute(dt, dt + calculation_step)
        added_count += await redis.geoadd(dt.isoformat(' '), *chain.from_iterable(coords))

    deleted_start, deleted_end, deleted_count = None, None, 0
    if clear_old:
        deleted_count, deleted_start, deleted_end = await clear_old_coords(redis)

    return start_dt, end_dt, added_count, deleted_start, deleted_end, deleted_count
