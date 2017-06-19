# -*- coding: utf-8 -*-
from datetime import datetime

import requests

URL = 'http://iss-positioner.nkoshelev.tech/lst'
# URL = 'http://localhost:8081/lst'

PARAMS = dict(start_dt='2017-06-12',
              end_dt='2017-07-07 17:20:22',
              dist='250',
              units='km',
              min_duration='30')
FILES = dict(lst=open('uragan.lst', 'rb'))


def main():
    start = datetime.utcnow()
    resp = requests.post(URL, data=PARAMS, files=FILES)
    result = resp.json()
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
    main()
