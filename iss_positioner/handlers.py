# -*- coding: utf-8 -*-
import asyncio
import ujson
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
from functools import partial
from itertools import chain
from json import JSONDecodeError

from aiohttp import web
from dateutil import parser as dt_parser

from iss_positioner.calculations import async_sun_angle
from .log import logger
from .redis import geo_radius, get_coords
from .util import datetime_range, load_html, read_lst, parse_filters

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
            return await self.compute_coords(start_dt=start_dt, end_dt=end_dt)
        return await self.get_coords(start_dt=start_dt, end_dt=end_dt, step=1)

    async def coords_range(self, data):
        _validate_requires({'start_dt', 'end_dt'}, data, is_body=False)
        dts = dt_parser.parse(data.pop('start_dt')), dt_parser.parse(data.pop('end_dt'))
        step = data.get('step', 1)
        start_dt, end_dt = min(dts), max(dts)
        today = datetime(*datetime.today().timetuple()[:3])

        if start_dt < today:
            if end_dt < today:
                return await self.compute_coords(start_dt, end_dt, step=step)

            coords = await asyncio.gather(self.compute_coords(start_dt, today, step),
                                          self.get_coords(start_dt=today, end_dt=end_dt, step=step),
                                          loop=self.request.app.loop)
            return chain.from_iterable(coords)

        return await self.get_coords(start_dt=start_dt, end_dt=end_dt, step=step)

    async def get_coords(self, **params):
        return await get_coords(self.request.app['redis'], loop=self.request.app.loop, **params)

    async def compute_coords(self, start_dt, end_dt, step=1):
        satellite = self.request.app['satellite']
        filters = {"dt": {"$gte": (start_dt - timedelta(days=1)).isoformat(), "$lte": end_dt.isoformat()}}
        satellite.tle_db = (tle['extra_info'] for tle in await self.request.app['get_tle'](filters=filters))
        coords = await satellite.compute(start_dt, end_dt, step)
        return [dict(dt=dt, coords=dict(longitude=lon, latitude=lat)) for lon, lat, dt in coords]


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
                      min_duration=data.get('min_duration'),
                      sun_angle=data.get('sun_angle'))

        return await self.get_results({}, **params)

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
                      dist=data.get('dist', 155),
                      units=data.get('units', 'km'),
                      min_duration=data.get('min_duration'),
                      sun_angle=data.get('sun_angle'))
        return await self.get_results(*objects, **params)

    async def intersect(self, **params):
        return await compute_intersect(self.request.app['redis'], loop=self.request.app.loop, **params)

    async def get_results(self, *objects, **params):
        sa_filters = params.pop('sun_angle', None)

        sessions = defaultdict(list)
        for obj in objects:
            obj.update(params)
            title = obj.get('title', (obj['lon'], obj['lat']))
            coords_set = await self.intersect(**obj)
            for coords in coords_set:
                traverse = min(coords, key=lambda c: c['dist'])
                sa = await async_sun_angle(traverse['dt'], **traverse['coord'])
                if parse_filters(sa, sa_filters):
                    sessions[traverse['dt'][:10]].append(dict(title=title,
                                                              sun_angle=sa,
                                                              start=coords[0],
                                                              traverse=traverse,
                                                              end=coords[-1],
                                                              coords=coords))

        sessions = ((k, sorted(v, key=lambda x: (x['traverse']['dt'], x['title']))) for k, v in sessions.items())
        return OrderedDict(sorted(sessions, key=lambda item: item[0]))


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

        try:
            sun_angle = ujson.loads(data['sun_angle'])
        except:
            sun_angle = None

        params = dict(start_dt=start_dt,
                      end_dt=end_dt,
                      dist=float(data.get('dist', 155)),
                      units=data.get('units', 'km'),
                      min_duration=int(data.get('min_duration', 1)),
                      sun_angle=sun_angle)

        return await self.get_results(*objects, **params)


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


async def find_traverse():
    return
