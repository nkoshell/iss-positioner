# -*- coding: utf-8 -*-
from datetime import datetime
from pprint import pprint

import requests

URL = 'http://iss-positioner.nkoshelev.tech/radius'

# Crimea
lon, lat = 34.6, 45.2

objects = [
    {'title': 'Crimea', 'lon': lon, 'lat': lat},
    {'title': 'Ozero Baikal', 'lon': 107.75, 'lat': 53.216},
    {'title': 'Lednik Davidova', 'lon': 78.15, 'lat': 41.86},
]

now = datetime.utcnow()


def get(params):
    start = datetime.utcnow()
    resp = requests.post(URL, json=params)
    result = resp.json()
    print(datetime.utcnow() - start)
    if result['error']:
        return
    return result['data']


def main():
    params_one = dict(start_dt=now.isoformat(), end_dt='2017-07-14', lat=lat, lon=lon, min_duration=30)
    result_one = get(params_one)
    print('One\n---')
    pprint(result_one)
    params_many = dict(start_dt=now.isoformat(), end_dt='2017-07-14', objects=objects, min_duration=30)
    result_many = get(params_many)
    print('Many\n----')
    pprint(result_many)


if __name__ == '__main__':
    main()
