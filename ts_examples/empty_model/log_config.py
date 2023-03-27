import logging

from typing import Dict


# https://stackoverflow.com/a/68672268
class DefaultExtrasAdapter(logging.LoggerAdapter):
    def __init__(self, logger, extra):
        super(DefaultExtrasAdapter, self).__init__(logger, extra)

    def process(self, msg, kwargs):
        # Speed gain if no extras are present
        if "extra" in kwargs and kwargs["extra"] is not None:
            copy = dict(self.extra).copy()
            copy.update(kwargs["extra"])
            kwargs["extra"] = copy
        else:
            kwargs["extra"] = self.extra
        return msg, kwargs


def get_logger(name: str, level: str) -> logging.Logger:
    level = level.upper()
    assert level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    log_format = (
        "{"
        '"timestamp": "%(asctime)s.%(msecs)03dZ", '
        '"requestId": "%(requestId)s", '
        '"level": "%(levelname)s", '
        '"loggerName": "%(name)s", '
        '"filename": "%(filename)s", '
        '"line": %(lineno)d, '
        '"func": "%(funcName)s", '
        '"message": "%(message)s"'
        "}"
    )
    date_format = "%Y-%m-%dT%H:%M:%S"

    # basic logger configuration
    logger = logging.getLogger(name)
    logger.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    # override extra 'requestId' field
    extra = {"requestId": "no-request-id"}
    logger = DefaultExtrasAdapter(logger, extra)
    return logger


def log_extra_req_id(req_id: str) -> Dict[str, str]:
    return {"requestId": req_id}


def main(raw_args=None):
    logger = get_logger(name=__name__, level="DEBUG")
    logger.debug({"my_msg": "With defaults"})
    logger.info({"my_msg": "With extra"}, extra={"requestId": "3.10"})
    logger.warning({"my_msg": "With extra"}, extra={"requestId": "0"})
    return


if __name__ == "__main__":
    main()
