# -*- coding: utf-8 -*-
import traceback
import ujson
from functools import partial

from aiohttp import web

__all__ = (
    'json_response_middleware',
)

json_response = partial(web.json_response, dumps=ujson.dumps)


def json_error(reason, status=500):
    return json_response({'error': True, 'error_msg': reason, 'data': None}, status=status)


def json_success(data):
    return json_response({'error': False, 'error_msg': None, 'data': data})


async def json_response_middleware(app, handler):
    async def middleware_handler(request):
        try:
            data = await handler(request)
            return data if isinstance(data, web.Response) else json_success(data)
        except web.HTTPException as exc:
            return json_error(exc.reason, exc.status_code)
        except:
            return json_error(traceback.format_exc())

    return middleware_handler
