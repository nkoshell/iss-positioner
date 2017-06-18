# -*- coding: utf-8  -*-
import asyncio
from aiohttp import ClientSession

from .log import logger
from .redis import fill_db

__all__ = (
    'listen_tle_storage',
    'listen_tle_queue',
)


async def listen_tle_queue(queue, channel, redis, satellite, *, tle_getter=None):
    while True:
        msg = await queue.get()
        try:
            if msg.get('stored'):
                result = await fill_db(redis, satellite, tle_getter)
                added_from, added_to, added, deleted_from, deleted_to, deleted = result
                for client in channel:
                    try:
                        await client.send_json({
                            'added': {
                                'count': added,
                                'from': added_from.isoformat(' '),
                                'to': added_to.isoformat(' '),
                            },
                            'updated': {
                                'from': added_from.isoformat(' '),
                                'to': added_to.isoformat(' '),
                            },
                            'deleted': {
                                'count': deleted,
                                'from': deleted_from.isoformat(' '),
                                'to': deleted_to.isoformat(' '),
                            }
                        })
                    except Exception as exc:
                        logger.exception(exc)
        except Exception as exc:
            logger.exception(exc)
        finally:
            queue.task_done()


async def listen_tle_storage(ws_url, queue, *, loop=None):
    try:
        async with ClientSession(loop=loop) as session:
            async with session.ws_connect(ws_url) as ws:
                while True:
                    msg = await ws.receive_json()
                    if msg.pop('channel', None) == 'tle:nasa:update':
                        logger.info('TLE from NASA have been updated: %s', msg)
                        await queue.put(msg)
    except Exception as exc:
        logger.exception(exc)

        await asyncio.sleep(5)
        logger.info('Try reconnect to "%s"', ws_url)
        await listen_tle_storage(ws_url, queue, loop=loop)
