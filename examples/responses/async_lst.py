# -*- coding: utf-8 -*-
import asyncio
import json
from datetime import datetime, timedelta

from aiohttp import ClientSession

URL = 'http://iss-positioner.nkoshelev.tech/lst'
NOW = datetime.utcnow()

PARAMS = dict(start_dt=NOW.isoformat(),
              end_dt=(NOW + timedelta(days=21)).isoformat(),
              dist='155',
              units='km',
              sun_angle=json.dumps({'$between': [1, 90]}),
              lst=open('uragan.lst', 'rb'))


async def main(loop):
    start = datetime.utcnow()
    async with ClientSession(loop=loop) as session:
        async with session.post(URL, data=PARAMS) as resp:
            result = await resp.json()

    print(datetime.utcnow() - start)

    if result['error']:
        return

    for dt, sessions in result['data'].items():
        print()
        print(dt)
        print('-' * len(dt))
        for session in sessions:
            print('Session duration', len(session['coords']), 'Traverse:', session['traverse'])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main(loop))
    finally:
        loop.close()
