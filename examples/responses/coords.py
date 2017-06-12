# -*- coding: utf-8 -*-
from datetime import datetime
from pprint import pprint

import requests

URL = 'http://iss-positioner.nkoshelev.pro/coords'


def get(params):
    start = datetime.utcnow()
    resp = requests.post(URL, json=params)
    result = resp.json()
    print(datetime.utcnow() - start)
    if result['error']:
        return
    return result['data']


def main():
    params_one = dict(dt='2017-07-01 23:43:15')
    params_many = dict(start_dt='2017-06-09', end_dt='2017-06-14', step=60)
    result_one = get(params_one)
    print('One\n---')
    pprint(result_one)
    result_many = get(params_many)
    print('Many\n----')
    pprint(result_many)


if __name__ == '__main__':
    main()
