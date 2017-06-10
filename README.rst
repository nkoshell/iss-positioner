Requirements
------------

- aiohttp >= 2.1.0
- aioredis >= 0.3.1
- dateutils >= 0.6.6
- pyaml >= 16.12.2
- pyephem >= 3.7.6.0
- tqdm >= 4.14.0
- ujson >= 1.35

Extra
-----

- redis


Installing
----------

::

    pip install iss-positioner


Getting started
---------------

Start aiohttp application:

.. code-block:: python

    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-
    import logging
    import os

    from aiohttp.web import run_app

    from iss_positioner import ISSPositionerService, util, LOG_FORMAT

    DIR = os.path.join(os.path.dirname(__file__))
    CFG = util.load_cfg(path=os.path.join(DIR, 'iss-positioner.yml'))

    if __name__ == '__main__':
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
        app = ISSPositionerService(config=CFG)
        run_app(app, port=80)


Usage examples
--------------

With using `httpie` package
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Subsat point for date and time::

   $ http POST iss-positioner.nkoshelev.pro/coords dt='2017-07-01 17:20:23'
    HTTP/1.1 200 OK
    Content-Length: 133
    Content-Type: application/json; charset=utf-8
    Date: Sat, 10 Jun 2017 22:36:34 GMT
    Server: Python/3.6 aiohttp/2.1.0

    {
        "data": [
            {
                "coords": {
                    "latitude": 29.1957281567,
                    "longitude": -60.4502132535
                },
                "dt": "2017-07-01 17:20:23"
            }
        ],
        "error": false,
        "error_msg": null
    }


Subsat points for date and time range::

    $ http POST iss-positioner.nkoshelev.pro/coords start_dt='2017-07-01 17:20:23' end_dt='2017-07-02 00:30:12' step:=3600
    HTTP/1.1 200 OK
    Content-Length: 590
    Content-Type: application/json; charset=utf-8
    Date: Sat, 10 Jun 2017 22:36:06 GMT
    Server: Python/3.6 aiohttp/2.1.0

    {
        "data": [
            {
                "coords": {
                    "latitude": -45.0957399616,
                    "longitude": 83.1269171834
                },
                "dt": "2017-07-01 18:00:00"
            },
            {
                "coords": {
                    "latitude": 8.7403712481,
                    "longitude": -66.4947965741
                },
                "dt": "2017-07-01 19:00:00"
            },
            {
                "coords": {
                    "latitude": 31.6325051557,
                    "longitude": 134.4496509433
                },
                "dt": "2017-07-01 20:00:00"
            },
            {
                "coords": {
                    "latitude": -51.320569018,
                    "longitude": 8.3954402804
                },
                "dt": "2017-07-01 21:00:00"
            },
            {
                "coords": {
                    "latitude": 24.0613209347,
                    "longitude": -125.9571602941
                },
                "dt": "2017-07-01 22:00:00"
            },
            {
                "coords": {
                    "latitude": 16.9217895882,
                    "longitude": 73.4462991357
                },
                "dt": "2017-07-01 23:00:00"
            }
        ],
        "error": false,
        "error_msg": null
    }

Find subsat points in radius::

    $ http POST iss-positioner.nkoshelev.pro/radius start_dt="2017-06-11 17:20:23" end_dt="2017-06-20 03:30:12" lon:=107.75 lat:=53.216 dist:=250 min_duration:=50
    HTTP/1.1 200 OK
    Content-Length: 7526
    Content-Type: application/json; charset=utf-8
    Date: Sat, 10 Jun 2017 22:38:05 GMT
    Server: Python/3.6 aiohttp/2.1.0

    {
        "data": [
            [
                {
                    "coord": {
                        "latitude": 51.615554797,
                        "longitude": 105.1945182681
                    },
                    "dist": 248.4514,
                    "dt": "2017-06-13 09:16:18",
                    "geohash": 4237098244661499,
                    "units": "km"
                },
                {
                    "coord": {
                        "latitude": 51.6165103869,
                        "longitude": 105.294688046
                    },
                    "dist": 243.6823,
                    "dt": "2017-06-13 09:16:19",
                    "geohash": 4237100216360980,
                    "units": "km"
                },
                {
                    "coord": {
                        "latitude": 51.6173747268,
                        "longitude": 105.3948578238
                    },
                    "dist": 239.0189,
                    "dt": "2017-06-13 09:16:20",
                    "geohash": 4237100762078023,
                    "units": "km"
                },

                ...

                 {
                    "coord": {
                        "latitude": 51.5499688871,
                        "longitude": 110.1997938752
                    },
                    "dist": 248.9689,
                    "dt": "2017-06-13 09:17:08",
                    "geohash": 4239262562588108,
                    "units": "km"
                }
            ]
        ],
        "error": false,
        "error_msg": null
    }

Find subsat points in radius for few objects::

    $ http POST iss-positioner.nkoshelev.pro/radius start_dt="2017-06-11 17:20:23" end_dt="2017-06-15 03:30:12" objects:='[{"title": "Baku", "lat": 40.46, "lon": 49.83}, {"title": "Ozero Baikal", "lon": 107.75, "lat": 53.216}]'  dist:=250 min_duration:=70
    HTTP/1.1 200 OK
    Content-Length: 10530
    Content-Type: application/json; charset=utf-8
    Date: Sat, 10 Jun 2017 22:43:05 GMT
    Server: Python/3.6 aiohttp/2.1.0

    {
        "data": {
            "Baku": [
                [
                    {
                        "coord": {
                            "latitude": 41.9817437673,
                            "longitude": 47.6533403993
                        },
                        "dist": 248.5992,
                        "dt": "2017-06-12 16:25:57",
                        "geohash": 3612423003133645,
                        "units": "km"
                    },
                    {
                        "coord": {
                            "latitude": 41.9460624976,
                            "longitude": 47.7219083905
                        },
                        "dist": 241.734,
                        "dt": "2017-06-12 16:25:58",
                        "geohash": 3612423083545812,
                        "units": "km"
                    },

                    ...

                    {
                        "coord": {
                            "latitude": 39.340457861,
                            "longitude": 52.3244825006
                        },
                        "dist": 246.5845,
                        "dt": "2017-06-12 16:27:08",
                        "geohash": 3613480324666665,
                        "units": "km"
                    }
                ]
            ],
            "Ozero Baikal": []
        },
        "error": false,
        "error_msg": null
    }

From LST file::

    $ http -f POST iss-positioner.nkoshelev.pro/lst start_dt='2017-06-11 17:20:23' end_dt='2017-06-12 03:30:12' dist=210 min_duration=60 lst@uragan.lst
    HTTP/1.1 200 OK
    Content-Length: 9444
    Content-Type: application/json; charset=utf-8
    Date: Sat, 10 Jun 2017 23:02:05 GMT
    Server: Python/3.6 aiohttp/2.1.0

    {
        "data": {
            "Abhzia": [],
            "Baku": [],
            "Cimlandskoe vodohran": [],
            "Crimea": [],
            "Don": [],
            "Kerchenski most": [],
            "Kergelen": [
                [
                    {
                        "coord": {
                            "latitude": -50.0511198281,
                            "longitude": 66.9441094995
                        },
                        "dist": 209.6767,
                        "dt": "2017-06-12 01:41:15",
                        "geohash": 2493333432573496,
                        "units": "km"
                    },
                    {
                        "coord": {
                            "latitude": -50.03455796,
                            "longitude": 67.0373216271
                        },
                        "dist": 202.8507,
                        "dt": "2017-06-12 01:41:16",
                        "geohash": 2493335234106988,
                        "units": "km"
                    },

                    ...

                    {
                        "coord": {
                            "latitude": -48.9167839496,
                            "longitude": 72.4097970128
                        },
                        "dist": 209.4392,
                        "dt": "2017-06-12 01:42:15",
                        "geohash": 2517761003506213,
                        "units": "km"
                    }
                ]
            ],
            "Lednik Davidova": [],
            "Magellanov proliv": [],
            "Ostrov Darvin": [],
            "Ostrov Herd": [],
            "Ozero Baikal": [],
            "Pamir1": [],
            "Pamir2": [],
            "Perito- Moreno": [],
            "Pulau Penida": [],
            "Razan12": [],
            "Razan3": [],
            "Razan4": [],
            "Razan5": [],
            "Reki chernogo mora1": [],
            "Reki chernogo mora2": [],
            "Reki chernogo mora3": [],
            "Samarskaya luka": [],
            "Ugra": [],
            "gora Hipsta": [],
            "ozero Rica": [],
            "ozero Sevan": [],
            "vUaskaran": []
        },
        "error": false,
        "error_msg": null
    }


Source code
-----------

The latest developer version is available in a github repository:
https://github.com/nkoshell/iss-positioner