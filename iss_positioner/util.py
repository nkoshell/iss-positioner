# -*- coding: utf-8 -*-
import asyncio
import operator
import os
import re
import ujson
from bisect import bisect_right
from datetime import datetime, timedelta
from functools import wraps

import yaml
from aiohttp import ClientSession

from .log import logger

__all__ = (
    'audit',
    'datetime_range',
    'find_le',
    'geo_member_to_dict',
    'get_tle',
    'load_cfg',
    'load_html',
    'periodic_task',
    'read_lst',
    'PROJECT_DIR',
)

PROJECT_DIR = os.path.join(os.path.dirname(__file__))
LST_EXP = re.compile(r'(?P<lon>[\d+-]+(\.)?\d+?)\s+(?P<lat>[\d+-]+(\.)?\d+?)\s+\'(?P<title>.+?)\'')


def audit(*args, **kwargs):
    def wrapper(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            dt = datetime.now()
            log.debug('Start execution `%s`', func.__name__)
            result = func(*args, **kwargs)
            log.debug('End execution `%s` (%s)', func.__name__, datetime.now() - dt)
            return result

        @wraps(func)
        async def async_inner_wrapper(*args, **kwargs):
            dt = datetime.now()
            log.debug('Start execution `%s`', func.__name__)
            result = await func(*args, **kwargs)
            log.debug('End execution `%s` (%s)', func.__name__, datetime.now() - dt)
            return result

        log = kwargs.pop('logger', logger)

        return async_inner_wrapper if asyncio.iscoroutinefunction(func) else inner_wrapper

    if args and kwargs:
        raise ValueError("cannot combine positional and keyword args")
    if len(args) == 1:
        return wrapper(args[0])
    elif len(args) != 0:
        raise ValueError("expected 1 argument, got %d", len(args))
    return wrapper


def datetime_range(start, end, step=None):
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        raise ValueError

    if not isinstance(step, timedelta):
        step = timedelta(seconds=step or 1)

    if start == end:
        yield start

    while start < end:
        yield start
        start += step


def find_le(a, x):
    """
    Find rightmost value less than or equal to x
    """
    i = bisect_right(a, x)
    if i:
        return a[i - 1]
    raise ValueError


async def get_tle(*, url=None, filters=None, loop=None):
    if not isinstance(filters, dict):
        d = datetime.today().date() - timedelta(days=1)
        filters = {"dt": {"$gte": d.isoformat()}, "norad_cat_id": 25544}

    query = {
        "filters": ujson.dumps(filters),
        "order": "dt",
        "only": "id,source,extra_info"
    }
    async with ClientSession(loop=loop) as session:
        async with session.get(url, params=query) as resp:
            r = await resp.json(loads=ujson.loads)
    return r.get('data')


def geo_member_to_dict(geo_member, *, units=None):
    return dict(dt=geo_member.member,
                dist=geo_member.dist,
                units=units,
                geohash=geo_member.hash,
                coord=geo_member.coord._asdict())


def load_html(*, name='index', path=None):
    if not isinstance(path, str):
        path = os.path.join(PROJECT_DIR, 'html', '{}.{}'.format(name, 'html'))

    if not os.path.exists(path):
        raise FileNotFoundError

    with open(path, 'r') as html:
        return html.read()


def load_cfg(*, filename='dev', path=None):
    if not isinstance(path, str):
        path = os.path.join(PROJECT_DIR, 'config', '{}.{}'.format(filename, 'yaml'))

    if not os.path.exists(path):
        raise FileNotFoundError

    with open(path, 'r') as cfg:
        return yaml.safe_load(cfg)


def periodic_task(delay):
    def wrapper(coroutine):
        @wraps(coroutine)
        async def runner(*args, **kwargs):
            while True:
                await coroutine(*args, **kwargs)
                await asyncio.sleep(delay)

        return runner

    return wrapper


def read_lst(lst, encoding='cp866'):
    if isinstance(lst, bytes):
        lst = lst.decode(encoding)
    objects = []
    for m in LST_EXP.finditer(lst):
        m = m.groupdict()
        m.update(lat=float(m['lat']), lon=float(m['lon']))
        objects.append(m)
    return objects


def parse_filters(value, filters):
    operators = {
        '$lt': lambda x: operator.lt(value, x),
        '$lte': lambda x: operator.le(value, x),
        '$eq': lambda x: operator.eq(value, x),
        '$ne': lambda x: operator.ne(value, x),
        '$gte': lambda x: operator.ge(value, x),
        '$gt': lambda x: operator.gt(value, x),
        '$between': lambda x: operator.ge(value, x[0]) and operator.le(value, x[-1])
    }

    if isinstance(filters, dict):
        return all(operators[k](v) for k, v in filters.items() if k in operators)
    return True
