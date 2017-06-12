# -*- coding: utf-8 -*-
import asyncio
from collections import defaultdict
from functools import partial
from itertools import chain

from aiohttp import web, WSCloseCode
from aioredis import create_reconnecting_redis

from .calculations import AsyncSatellite
from .handlers import subscribe, index, CoordsApi, RadiusApi, LST
from .middlewares import json_response_middleware
from .tasks import listen_tle_queue, listen_tle_storage
from .util import get_tle

__all__ = (
    'ISSPositionerService',
)


async def start_background_tasks(app):
    tle_storage_conf = app['config']['tle-storage'].copy()
    redis_params = app['config']['redis'].copy()
    redis_addres = redis_params.pop('host', 'localhost'), redis_params.pop('port', 6379)

    app['get_tle'] = partial(get_tle, url=tle_storage_conf['query_url'], loop=app.loop)

    app['satellite'] = AsyncSatellite(loop=app.loop)
    app['redis'] = await create_reconnecting_redis(redis_addres, **redis_params, loop=app.loop)

    if app['config']['on-startup']['redis']['flush']:
        await app['redis'].flushall()

    tle_storage_listener = listen_tle_storage(tle_storage_conf['listen_url'], app['queue'], loop=app.loop)
    tle_queue_listener = listen_tle_queue(app['queue'], app['channels']['coords'],
                                          app['redis'], app['satellite'],
                                          tle_getter=app['get_tle'])

    app['tle_storage_listener'] = app.loop.create_task(tle_storage_listener)
    app['tle_queue_listener'] = app.loop.create_task(tle_queue_listener)

    if app['config']['on-startup']['redis']['fill']:
        app['queue'].put_nowait(dict(stored=True))


async def cleanup_background_tasks(app):
    app['tle_storage_listener'].cancel()
    app['tle_queue_listener'].cancel()

    await app['tle_storage_listener']
    await app['tle_queue_listener']


async def on_shutdown(app):
    clients = chain.from_iterable(app['channels'].values())
    fs = (ws.close(code=WSCloseCode.GOING_AWAY, message='Server shutdown') for ws in clients)
    await asyncio.gather(*fs, loop=app.loop)


class ISSPositionerService(web.Application):
    def __init__(self, *, config=None, **kwargs):
        if not isinstance(config, dict):
            raise ValueError('Argument `config` must be dict()')

        super().__init__(**kwargs)

        self.middlewares.append(json_response_middleware)

        self['config'] = config
        self['channels'] = defaultdict(set)
        self['queue'] = asyncio.Queue()

        self.on_startup.append(start_background_tasks)
        self.on_cleanup.append(cleanup_background_tasks)

        self.router.add_get('/', index)
        self.router.add_get('/subscribe/{channel}', subscribe)

        self.router.add_route('*', '/lst', LST)
        self.router.add_route('*', '/coords', CoordsApi)
        self.router.add_route('*', '/radius', RadiusApi)
