import logging
import re

from sys import _getframe, stderr
from typing import Literal

from loguru import logger, _colorizer

from constants import BotConstants

_logger = logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = _getframe(6), 6
        while frame and frame.f_code.co_filename == __file__:
            frame = frame.f_back
            depth += 1

        (
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
        )


def log_message(*, function_name: str, message: str, level: Literal["DEBUG", "INFO"] = "INFO", args=(), kwargs={}) -> None:
    # this function make me able to format messages using tag colors
    # eg:
    # "<red>Test</> <yellow>Snipy#7374 - 7104....</> used ...."
    # this is more cool than using colorama and other shit
    _levels = {"DEBUG": logger.debug, "INFO": logger.info,} # TO DO: add the other log levels
    message = f"<cyan>:</><blue>{function_name}</><cyan>:</> - {message}"
    colorizer = _colorizer.Colorizer()
    prepared_message = colorizer.prepare_message(message, args, kwargs)

    _levels[level](prepared_message.colorize(0))


def escape_ansi_codes(string: str) -> str:
    # this functions is the exact same function used in the monkeypatch
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub('', string)  


def setup_logging():
    logger.remove()
    try:
        logger.add(stderr, level=BotConstants.log_level, colorize=True)
    except AttributeError:
        logger.add(stderr, level="DEBUG")
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
