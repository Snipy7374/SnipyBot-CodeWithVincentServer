from datetime import datetime
from pathlib import Path
import os
import json
import re
from time import perf_counter_ns

from typing import Any

from disnake.ext import commands
from disnake import (
    Intents,
    Game,
    AllowedMentions,
    Status,
    AppCmdInter
)

import aiofiles

from constants import BotConstants
from _logging import setup_logging, log_message, _logger
from slash_commands.languages_select import DropdownViewRoles
from slash_commands.system_roles_dropdown import DropdownViewSystem, ButtonView
from slash_commands.roles_giver import DropdownView
from monkey_patches import apply_monkey_patch


class SnipyBot(commands.Bot):
    """My custom Bot subclass"""
    def __init__(self) -> None:
        allowed_mentions: AllowedMentions = AllowedMentions(
            everyone=False,
            replied_user=True,
            roles=True,
            users=True
        )

        super().__init__(
            command_prefix=commands.when_mentioned, 
            help_command=None, # type: ignore
            intents=Intents.default(),
            activity=Game(name="Commands: mention me!"),
            allowed_mentions=allowed_mentions,
            owner_id=710570210159099984,
            reload=True,
            status=Status.streaming,
            )

        self.logger = _logger
        self.logging_level = BotConstants.log_level
        setup_logging()

        # note that i'm monkeypatching the library
        # monkeypatched files:
        #
        # _logger.py - line 1964:
        #
        # for handler in core.handlers.values():
        #    if isinstance(handler._sink, FileSink):
        #        actual_msg = log_record["message"]
        #        log_record["message"] = self._escape_ansi_codes(actual_msg)
        #        handler.emit(log_record, level_id, from_decorator, raw, None)
        #        return
        #    handler.emit(log_record, level_id, from_decorator, raw, colored_message)
        #
        #
        # the function below helps me to remove the ANSI codes from the logs messages to
        # write in the log file
        # _logger.py - line 1972:
        #
        #    def _escape_ansi_codes(self, string: str) -> str:
        #       ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        #       return ansi_escape.sub('', string)
        #
        #
        # this monkeypatch permit to output non colorized messages to the log file and to
        # output colorized output file to terminal
        # i need to do this since i can't manage in any other way how messages are sent to
        # specific handlers
        self.logger.add(
            BotConstants.log_file_path,
            level=self.logging_level,
            format=BotConstants.log_file_message_format,
            filter=self.__log_filter, # teorically this is not needed but i'll keep this so if an ANSI code was not cathed by the regex it'll not be writed in the log file
            colorize=False,
            enqueue=True,
            rotation=BotConstants.log_file_rotation,
            retention=BotConstants.log_file_retention,
            compression=BotConstants.log_file_compression,
        )
        self._handlers = self.logger._core.handlers # type: ignore
        self.TOKEN: str = BotConstants.token
        self.my_extensions: set[str] = {"cogs", "slash_commands"}
        self.github_repo: str = BotConstants.github_repository
        self.ignore_files: list[str] = ["__init__.py",]
        self._before_slash_command_invoke = self.my_before_slash_command_invoke
        self._after_slash_command_invoke = self.my_after_slash_command_invoke
        apply_monkey_patch()

    def __log_filter(self, record) -> bool:
        # filter to not output colorized messages
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return not any(ansi_escape.findall(record["message"]))  
    
    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as {self.user}  -  latency {self.latency}")
        log_message(function_name=self.on_ready.__qualname__, message="<red>Test</>", level="INFO")

    async def start(self, *, reconnect: bool = True) -> None:
        self.logger.info(f"Starting the bot at {datetime.utcnow()}")
        # This function is similar to a Setup_hook function
        # call setups here database connections etc...
        self.load_exts()
        await self.load_json_info()
        self.uptime_start: datetime = datetime.utcnow()
        self.add_persistent_views()

        await super().start(self.TOKEN, reconnect=reconnect)

    async def my_before_slash_command_invoke(self, inter) -> None:
        inter.start_time = perf_counter_ns()
    
    async def my_after_slash_command_invoke(self, inter: AppCmdInter) -> None:
        exec_time = (perf_counter_ns() - inter.start_time) / 1e+9 # type: ignore
        log_message(function_name=self.my_after_slash_command_invoke.__qualname__, message=f"<Y>{inter.author}</> - <Y>{inter.author.id}</> | {inter.guild} - {inter.guild_id} | Command <r>{inter.application_command.name}</> was executed in <g>{exec_time}s</>", level="INFO")

        if (original_msg:=await inter.edit_original_response()).embeds and hasattr(inter, "latest_videos_embeds"):
            for embed in inter.latest_videos_embeds: # type: ignore
                embed.set_footer(text=f"{embed.footer.text} | Executed in {exec_time}s")
            for embed in original_msg.embeds:
                embed.set_footer(text=f"{embed.footer.text} | Executed in {exec_time}s")
            await inter.edit_original_message(embeds=original_msg.embeds)

        elif (original_msg:=await inter.original_response()).embeds:
            for embed in original_msg.embeds:
                embed.set_footer(text=f"Executed in {exec_time}s")
            await inter.edit_original_message(embeds=original_msg.embeds)

    
    def add_persistent_views(self) -> None:
        self.logger.info(f"{datetime.utcnow()}:Loading persistent views")
        self.add_view(DropdownView())
        self.add_view(DropdownViewRoles())
        self.add_view(DropdownViewSystem())
        self.add_view(ButtonView())

    def load_exts(self) -> None:
        for i in self.my_extensions:
            if os.path.isdir(f"{i}"):
              for file in os.listdir(f"{i}"):
                if file.endswith(".py") and file not in self.ignore_files:
                  super().load_extension(f"{i}.{file[:-3]}")
                  self.logger.info(f"{file} extension path was loaded succesfully")
    
    async def load_json_info(self) -> None:
        json_path: Path = Path("config.json")
        async with aiofiles.open(json_path, "r") as f:
            content = await f.read()
        json_data: dict[str, Any] = json.loads(content)

        self.json_info = json_data
