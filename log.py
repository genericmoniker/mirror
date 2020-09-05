import logging
import os
import sys


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_get_log_formatter())
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


def _get_log_formatter():
    # If running under systemd, use a simple format since the journal
    # adds its own metadata (including, for example, the date/time).
    if os.getppid() == 1:
        fmt = "%(levelname)7s %(message)s"
    else:
        fmt = "%(asctime)s [%(thread)d] %(levelname)1.1s %(message)s"
    return logging.Formatter(fmt)
