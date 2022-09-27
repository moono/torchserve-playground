from pydantic import BaseModel

BASE_LOG_FORMAT = (
    '"timestamp": "%(asctime)s.%(msecs)03dZ", '
    '"level": "%(levelname)s", '
    '"loggerName": "%(name)s", '
    '"filename": "%(filename)s", '
    '"line": %(lineno)d, '
    '"func": "%(funcName)s"'
)
LOG_FORMAT = f'{{{BASE_LOG_FORMAT}, "message": "%(message)s"}}'


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "json": {
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    }
    handlers = {
        "custom_console": {
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers = {}


def gen_log_config(logger_name: str, level: str):
    base_config = LogConfig().dict()
    base_config["loggers"][logger_name] = {
        "handlers": ["custom_console"],
        "level": level,
        "propagate": False,
    }
    return base_config