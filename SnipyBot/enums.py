from enum import Enum

from loguru import logger

__all__ = ("LogLevel",)


class LogLevel(Enum):
    TRACE = logger.trace
    DEBUG = logger.debug
    INFO = logger.info
    SUCCESS = logger.success
    WARNING = logger.warning
    ERROR = logger.error
    CRITICAL = logger.critical