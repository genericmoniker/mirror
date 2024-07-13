"""Logging configuration."""

from copy import deepcopy

from uvicorn.config import LOGGING_CONFIG


def uvicorn_log_config() -> dict:
    config = deepcopy(LOGGING_CONFIG)
    default_fmt = "%(asctime)s %(levelprefix)s %(name)s -> %(message)s"
    config["formatters"]["default"]["fmt"] = default_fmt
    access_fmt = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'  # noqa: E501
    config["formatters"]["access"]["fmt"] = access_fmt

    config["loggers"] = {
        # Set the root handler so we have the same format for all log messages:
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    }
    return config
