# -*- coding: utf-8 -*-
import io
import logging
from functools import partial

from tqdm import tqdm

LOG_FORMAT = '[%(levelname)1.1s %(asctime)s %(name)s %(module)s:%(lineno)i] %(message)s'
logger = logging.getLogger('iss_positioner')


__all__ = (
    'logger',
    'LOG_FORMAT',
)

class TqdmToLogger(io.StringIO):
    """
    Output stream for TQDM which will output to logger module instead of the StdOut.
    """
    buf = ''

    def __init__(self, log=logger, level=logging.INFO):
        super().__init__()
        self.logger = log
        self.level = level

    def write(self, buf):
        self.buf = buf.strip('\r\n')

    def flush(self):
        self.logger.log(self.level, self.buf)


tqdm = partial(tqdm, file=TqdmToLogger())
