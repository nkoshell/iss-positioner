# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime

from aiohttp import ClientSession

URL = 'http://iss-positioner.nkoshelev.tech/lst'

PARAMS = dict(start_dt='2017-06-12',
              end_dt='2017-07-07 17:20:22',
              dist='250',
              units='km',
              min_duration='30',
              lst=open('uragan.lst', 'rb'))


async def main(loop):
    start = datetime.utcnow()
    async with ClientSession(loop=loop) as session:
        async with session.post(URL, data=PARAMS) as resp:
            result = await resp.json()
            print(datetime.utcnow() - start)

            if result['error']:
                return

            for title, coords_set in result['data'].items():
                print()
                print(title)
                print('-' * len(title))
                for coords in coords_set:
                    print('Session duration', len(coords), 'Traverz:', min(coords, key=lambda c: c['dist']))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main(loop))
    finally:
        loop.close()
