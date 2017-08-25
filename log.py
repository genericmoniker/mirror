import logging
from logging.handlers import RotatingFileHandler

import os
import sys

logger = logging.getLogger()


def setup_logging(filename):
    fmt = '%(asctime)s [%(thread)d] %(levelname)1.1s %(message)s'
    formatter = logging.Formatter(fmt)
    if filename:
        setup_file(filename, formatter)
    setup_stream(formatter)


def setup_file(filename, formatter):
    log_dir = os.path.dirname(filename)
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(filename, maxBytes=10240, backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def setup_stream(formatter):
    strm_handler = logging.StreamHandler(sys.stdout)
    strm_handler.setFormatter(formatter)
    logger.addHandler(strm_handler)
    logger.setLevel(logging.INFO)
