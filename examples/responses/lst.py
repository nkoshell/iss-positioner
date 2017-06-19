# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

import requests

URL = 'http://iss-positioner.nkoshelev.tech/lst'
NOW = datetime.utcnow()

PARAMS = dict(start_dt=NOW.isoformat(),
              end_dt=(NOW + timedelta(days=21)).isoformat(),
              dist='250',
              units='km',
              sun_angle=json.dumps({'$between': [1, 90]}))
FILES = dict(lst=open('uragan.lst', 'rb'))


def main():
    start = datetime.utcnow()
    resp = requests.post(URL, data=PARAMS, files=FILES)
    result = resp.json()
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
    main()
