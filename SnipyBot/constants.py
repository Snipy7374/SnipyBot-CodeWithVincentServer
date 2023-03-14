from os import environ
from dotenv import load_dotenv
from datetime import datetime

from enums import LogLevel

load_dotenv("../.env")

__all__ = ("BotConstants",)


class BotConstants:
    name = "Snipy Bot"
    token = environ.get("TOKEN_BOT", "")
    log_level = environ.get("LOG_LEVEL", "DEBUG")
    log_file_path = f'{environ.get("LOG_FILE_PATH", "./logs/")}{datetime.strftime(datetime.now(), "%Y_%m_%d")}.txt'
    log_file_message_format = environ.get(
        "LOG_FILE_MESSAGE_FORMAT",
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}",
    )
    log_file_rotation = environ.get("LOG_FILE_ROTATION", "1 day")
    log_file_retention = environ.get("LOG_FILE_RETENTION", "1 week")
    log_file_compression = environ.get("LOG_FILE_COMPRESSION", "zip")
    github_repository = "https://github.com/Snipy7374/SnipyBot-CodeWithVincentServer"  # noqa: E501
