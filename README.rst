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

   $ http POST iss-positioner.nkoshelev.tech/coords dt='2017-07-01 17:20:23'
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

    $ http POST iss-positioner.nkoshelev.tech/coords start_dt='2017-07-01 17:20:23' end_dt='2017-07-02 00:30:12' step:=3600
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

    $ http POST iss-positioner.nkoshelev.tech/radius start_dt="2017-06-24 17:20:23" end_dt="2017-06-26 03:30:12" lon:=45.35 lat:=40.31 dist:=155 sun_angle:='{"$between": [1, 90]}'
    HTTP/1.1 200 OK
    Content-Length: 5233
    Content-Type: application/json; charset=utf-8
    Date: Mon, 19 Jun 2017 00:32:45 GMT
    Server: Python/3.6 aiohttp/2.1.0

    {
        "data": {
            "2017-06-25": [
                {
                    "coords": [
                        {
                            "coord": {
                                "latitude": 41.6560980011,
                                "longitude": 45.040654242
                            },
                            "dist": 151.9575,
                            "dt": "2017-06-25 11:33:25",
                            "geohash": 3612189142451081,
                            "units": "km"
                        },
                        {
                            "coord": {
                                "latitude": 41.620011176,
                                "longitude": 45.1084819436
                            },
                            "dist": 147.1127,
                            "dt": "2017-06-25 11:33:26",
                            "geohash": 3612189381935032,
                            "units": "km"
                        },
                        ...
                        {
                            "coord": {
                                "latitude": 40.5169486871,
                                "longitude": 47.1061268449
                            },
                            "dist": 150.4877,
                            "dt": "2017-06-25 11:33:56",
                            "geohash": 3612067477243933,
                            "units": "km"
                        }
                    ],
                    "end": {
                        "coord": {
                            "latitude": 40.5169486871,
                            "longitude": 47.1061268449
                        },
                        "dist": 150.4877,
                        "dt": "2017-06-25 11:33:56",
                        "geohash": 3612067477243933,
                        "units": "km"
                    },
                    "start": {
                        "coord": {
                            "latitude": 41.6560980011,
                            "longitude": 45.040654242
                        },
                        "dist": 151.9575,
                        "dt": "2017-06-25 11:33:25",
                        "geohash": 3612189142451081,
                        "units": "km"
                    },
                    "sun_angle": 53.0876931352,
                    "title": [
                        45.35,
                        40.31
                    ],
                    "traverse": {
                        "coord": {
                            "latitude": 41.073352933,
                            "longitude": 46.116220057
                        },
                        "dist": 106.697,
                        "dt": "2017-06-25 11:33:41",
                        "geohash": 3612029254672552,
                        "units": "km"
                    }
                }
            ]
        },
        "error": false,
        "error_msg": null
    }

Find subsat points in radius for few objects::

    $ http POST iss-positioner.nkoshelev.tech/radius start_dt="2017-06-24 17:20:23" end_dt="2017-06-26 03:30:12" objects:='[{"title": "Baku", "lat": 40.46, "lon": 49.83}, {"title": "Ozero Baikal", "lon": 107.75, "lat": 53.216}]' dist:=155 sun_angle:='{"$between": [1, 90]}'
    HTTP/1.1 200 OK
    Content-Length: 10241
    Content-Type: application/json; charset=utf-8
    Date: Mon, 19 Jun 2017 00:41:49 GMT
    Server: Python/3.6 aiohttp/2.1.0

    {
        "data": {
            "2017-06-25": [
                {
                    "coords": [
                        {
                            "coord": {
                                "latitude": 39.3338549124,
                                "longitude": 48.8792225718
                            },
                            "dist": 149.2349,
                            "dt": "2017-06-25 05:05:32",
                            "geohash": 3611733843357722,
                            "units": "km"
                        },
                        ...
                        {
                            "coord": {
                                "latitude": 40.8865059627,
                                "longitude": 51.5298727155
                            },
                            "dist": 151.0384,
                            "dt": "2017-06-25 05:06:13",
                            "geohash": 3614217228560593,
                            "units": "km"
                        }
                    ],
                    "end": {
                        "coord": {
                            "latitude": 40.8865059627,
                            "longitude": 51.5298727155
                        },
                        "dist": 151.0384,
                        "dt": "2017-06-25 05:06:13",
                        "geohash": 3614217228560593,
                        "units": "km"
                    },
                    "start": {
                        "coord": {
                            "latitude": 39.3338549124,
                            "longitude": 48.8792225718
                        },
                        "dist": 149.2349,
                        "dt": "2017-06-25 05:05:32",
                        "geohash": 3611733843357722,
                        "units": "km"
                    },
                    "sun_angle": 41.9252071823,
                    "title": "Baku",
                    "traverse": {
                        "coord": {
                            "latitude": 40.0998146954,
                            "longitude": 50.1561203599
                        },
                        "dist": 48.6902,
                        "dt": "2017-06-25 05:05:52",
                        "geohash": 3612624174040669,
                        "units": "km"
                    }
                },
                {
                    "coords": [
                        {
                            "coord": {
                                "latitude": 39.8750128105,
                                "longitude": 48.2068732381
                            },
                            "dist": 152.528,
                            "dt": "2017-06-25 11:34:13",
                            "geohash": 3612454092213748,
                            "units": "km"
                        },
                        ...
                        {
                            "coord": {
                                "latitude": 39.1050050778,
                                "longitude": 49.4737878442
                            },
                            "dist": 153.7554,
                            "dt": "2017-06-25 11:34:33",
                            "geohash": 3611782396693308,
                            "units": "km"
                        }
                    ],
                    "end": {
                        "coord": {
                            "latitude": 39.1050050778,
                            "longitude": 49.4737878442
                        },
                        "dist": 153.7554,
                        "dt": "2017-06-25 11:34:33",
                        "geohash": 3611782396693308,
                        "units": "km"
                    },
                    "start": {
                        "coord": {
                            "latitude": 39.8750128105,
                            "longitude": 48.2068732381
                        },
                        "dist": 152.528,
                        "dt": "2017-06-25 11:34:13",
                        "geohash": 3612454092213748,
                        "units": "km"
                    },
                    "sun_angle": 51.3293668014,
                    "title": "Baku",
                    "traverse": {
                        "coord": {
                            "latitude": 39.4919632142,
                            "longitude": 48.8440749049
                        },
                        "dist": 136.5807,
                        "dt": "2017-06-25 11:34:23",
                        "geohash": 3611732186127579,
                        "units": "km"
                    }
                }
            ]
        },
        "error": false,
        "error_msg": null
    }

From LST file::

    $ http -f POST iss-positioner.nkoshelev.tech/lst start_dt='2017-06-21 17:20:23' end_dt='2017-06-25 03:30:12' dist=155 sun_angle='{"$between":[60, 90]}' lst@uragan.lst
    HTTP/1.1 200 OK
    Content-Length: 2773
    Content-Type: application/json; charset=utf-8
    Date: Sun, 18 Jun 2017 23:18:07 GMT
    Server: Python/3.6 aiohttp/2.1.0
    
    {
        "data": {
            "2017-06-22": [
                {
                    "coords": [
                        {
                            "coord": {
                                "latitude": 46.3698428995,
                                "longitude": 42.7196744084
                            },
                            "dist": 153.2124,
                            "dt": "2017-06-22 07:42:05",
                            "geohash": 3707104453628981,
                            "units": "km"
                        },
                        ...
                        {
                            "coord": {
                                "latitude": 46.7598274929,
                                "longitude": 43.8530954719
                            },
                            "dist": 153.8867,
                            "dt": "2017-06-22 07:42:19",
                            "geohash": 3707422748292802,
                            "units": "km"
                        }
                    ],
                    "end": {
                        "coord": {
                            "latitude": 46.7598274929,
                            "longitude": 43.8530954719
                        },
                        "dist": 153.8867,
                        "dt": "2017-06-22 07:42:19",
                        "geohash": 3707422748292802,
                        "units": "km"
                    },
                    "start": {
                        "coord": {
                            "latitude": 46.3698428995,
                            "longitude": 42.7196744084
                        },
                        "dist": 153.2124,
                        "dt": "2017-06-22 07:42:05",
                        "geohash": 3707104453628981,
                        "units": "km"
                    },
                    "sun_angle": 61.0532714812,
                    "title": "Cimlandskoe vodohran",
                    "traverse": {
                        "coord": {
                            "latitude": 46.5663851782,
                            "longitude": 43.2842418551
                        },
                        "dist": 145.685,
                        "dt": "2017-06-22 07:42:12",
                        "geohash": 3707321610769135,
                        "units": "km"
                    }
                }
            ]
        },
        "error": false,
        "error_msg": null
    }


NikitaKoshelev-MacBook-Pro:responses nkoshelev$


Source code
-----------

The latest developer version is available in a github repository:
https://github.com/nkoshell/iss-positioner