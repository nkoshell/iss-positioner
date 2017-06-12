# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime
from pprint import pprint

from aiohttp import ClientSession

URL = 'http://iss-positioner.nkoshelev.pro/radius'

# Crimea
lon, lat = 34.6, 45.2

objects = [
    {'title': 'Crimea', 'lon': lon, 'lat': lat},
    {'title': 'Ozero Baikal', 'lon': 107.75, 'lat': 53.216},
    {'title': 'Lednik Davidova', 'lon': 78.15, 'lat': 41.86},
]

now = datetime.utcnow()


async def get(session, params):
    start = datetime.utcnow()
    async with session.post(URL, json=params) as resp:
        result = await resp.json()
    print(datetime.utcnow() - start)
    if result['error']:
        return
    return result['data']


async def main(loop):
    params_one = dict(start_dt=now.isoformat(), end_dt='2017-07-14', lat=lat, lon=lon, min_duration=30)
    params_many = dict(start_dt=now.isoformat(), end_dt='2017-07-14', objects=objects, min_duration=30)
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
