# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime, timedelta
from functools import partial
from json import JSONDecodeError

from aiohttp import web
from dateutil import parser as dt_parser

from .log import logger
from .redis import geo_radius, get_coords
from .util import datetime_range, load_html, read_lst

__all__ = (
    'index',
    'subscribe',
    'CoordsApi',
    'RadiusApi',
    'LST',
)


class CoordsApi(web.View):
    async def post(self):
        data = await get_json(self.request)
        if 'dt' in data:
            return await self.coords(data)
        return await self.coords_range(data)

    async def coords(self, data):
        start_dt = end_dt = dt_parser.parse(data.pop('dt'))
        if start_dt < datetime(*datetime.today().timetuple()[:3]):
            raise web.HTTPNotFound
        return await self.get_coords(start_dt=start_dt, end_dt=end_dt, step=1)

    async def coords_range(self, data):
        _validate_requires({'start_dt', 'end_dt'}, data, is_body=False)
        dts = dt_parser.parse(data.pop('start_dt')), dt_parser.parse(data.pop('end_dt'))
        start_dt, end_dt = min(dts), max(dts)
        if start_dt < datetime(*datetime.today().timetuple()[:3]):
            raise web.HTTPNotFound
        return await self.get_coords(start_dt=start_dt, end_dt=end_dt, step=data.get('step', 1))

    async def get_coords(self, **params):
        return await get_coords(self.request.app['redis'], loop=self.request.app.loop, **params)


class RadiusApi(web.View):
    async def post(self):
        data = await get_json(self.request)
        if 'objects' in data:
            return await self.radius_many(data)
        return await self.radius(data)

    async def radius(self, data):
        _validate_requires({'start_dt', 'end_dt', 'lat', 'lon'}, data)
        dts = dt_parser.parse(data.pop('start_dt')), dt_parser.parse(data.pop('end_dt'))
        start_dt, end_dt = min(dts), max(dts)
        if start_dt < datetime(*datetime.today().timetuple()[:3]):
            raise web.HTTPNotFound

        params = dict(start_dt=start_dt,
                      end_dt=end_dt,
                      lon=data['lon'],
                      lat=data['lat'],
                      dist=data.get('dist', 250),
                      units=data.get('units', 'km'),
                      min_duration=data.get('min_duration'))

        return await self.intersect(**params)

    async def radius_many(self, data):
        _validate_requires({'objects', 'start_dt', 'end_dt'}, data)

        objects = data['objects']
        if not isinstance(objects, list):
            raise web.HTTPBadRequest(reason='Body parameter `objects` must be `array`')
        object_keys = {'lat', 'lon'}
        if not all(object_keys.issubset(obj) for obj in objects):
            raise web.HTTPBadRequest(reason='Object inside array `objects` '
                                            'must contains required keys `{}`'.format(object_keys))

        dts = dt_parser.parse(data.pop('start_dt')), dt_parser.parse(data.pop('end_dt'))
        start_dt, end_dt = min(dts), max(dts)
        if start_dt < datetime(*datetime.today().timetuple()[:3]):
            raise web.HTTPNotFound

        params = dict(start_dt=start_dt,
                      end_dt=end_dt,
                      dist=data.get('dist', 250),
                      units=data.get('units', 'km'),
                      min_duration=data.get('min_duration'))
        return {obj.get('title', (obj['lon'], obj['lat'])): await self.intersect(**params, **obj) for obj in objects}

    async def intersect(self, **params):
        return await compute_intersect(self.request.app['redis'], loop=self.request.app.loop, **params)


class LST(RadiusApi):
    async def get(self):
        return web.Response(text=load_html(name='lst'), content_type='text/html')

    async def post(self):
        data = await self.request.post()
        _validate_requires({'start_dt', 'end_dt', 'lst'}, data)
        lst = data['lst']
        objects = read_lst(lst.file.read())

        dts = dt_parser.parse(data['start_dt']), dt_parser.parse(data['end_dt'])
        start_dt, end_dt = min(dts), max(dts)
        if start_dt < datetime(*datetime.today().timetuple()[:3]):
            raise web.HTTPNotFound

        params = dict(start_dt=start_dt,
                      end_dt=end_dt,
                      dist=float(data.get('dist', 250)),
                      units=data.get('units', 'km'),
                      min_duration=int(data.get('min_duration', 60)))
        return {obj.get('title', (obj['lon'], obj['lat'])): await self.intersect(**params, **obj) for obj in objects}


async def index(request):
    return web.Response(text=load_html(), content_type='text/html')


async def get_json(request):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise web.HTTPBadRequest(reason='Wrong JSON format')
    else:
        return data


def _validate_requires(required, iterable, *, is_body=True, msg=None):
    if not required.issubset(iterable):
        raise web.HTTPBadRequest(reason=msg or ('{} parameters must contains required keys `{}`'
                                                .format('Body' if is_body else 'Query', required)))


async def subscribe(request):
    channel_name = request.match_info['channel']
    channel = request.app['channels'][channel_name]
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    channel.add(ws)
    logger.debug('Someone joined to channel "{}".'.format(channel_name))

    try:
        while True:
            msg = await ws.receive_json()
            if msg.get('command') == 'close':
                await ws.close()
    except Exception as exc:
        logger.exception(exc)
    finally:
        channel.remove(ws)

    if ws.closed:
        channel.remove(ws)

    logger.debug('Websocket connection closed in channel "{}"'.format(channel_name))
    return ws


async def compute_intersect(redis, *, start_dt=None, end_dt=None, loop=None, **params):
    min_duration = params.pop('min_duration', None)
    rng = datetime_range(datetime(*start_dt.timetuple()[:4]), datetime(*end_dt.timetuple()[:4]), timedelta(hours=1))
    func = partial(geo_radius, redis=redis, **params)
    result = await asyncio.gather(*(func(dt=dt) for dt in rng), loop=loop)
    return filter(lambda val: len(val) > min_duration if min_duration else val, result)
