#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os

from aiohttp.web import run_app

from iss_positioner import ISSPositionerService, load_cfg, LOG_FORMAT

DIR = os.path.join(os.path.dirname(__file__))
CFG = load_cfg(path=os.path.join(DIR, 'iss-positioner.yml'))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    app = ISSPositionerService(config=CFG)
    run_app(app, port=80)
