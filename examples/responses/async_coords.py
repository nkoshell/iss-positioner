# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime
from pprint import pprint

from aiohttp import ClientSession

URL = 'http://iss-positioner.nkoshelev.tech/coords'


async def get(session, params):
    start = datetime.utcnow()
    async with session.post(URL, json=params) as resp:
        result = await resp.json()
    print(datetime.utcnow() - start)
    if result['error']:
        return
    return result['data']


async def main(loop):
    params_one = dict(dt='2017-07-01 23:43:15')
    params_many = dict(start_dt='2017-06-09', end_dt='2017-06-14', step=60)
    async with ClientSession(loop=loop) as session:
        result_one, result_many = await asyncio.gather(get(session, params_one), get(session, params_many), loop=loop)
    print('One\n---')
    pprint(result_one)
    print('Many\n----')
    pprint(result_many)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main(loop))
    finally:
        loop.close()
