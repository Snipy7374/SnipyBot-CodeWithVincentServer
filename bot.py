from datetime import datetime
from dotenv import load_dotenv
import aiofiles

from pathlib import Path
import os
import logging
import json

from typing import (
    Any,
    Dict,
    Optional,
    TYPE_CHECKING,
    Set
)


from disnake.ext import commands
from disnake import (
    Intents,
    Game,
    AllowedMentions,
    Status
)

from slashCommands.multiDropdown import DropdownViewRoles
from slashCommands.SystemDropdown import DropdownViewSystem, ButtonView
from slashCommands.roles_giver import DropdownView

logging.basicConfig(level=logging.INFO)
load_dotenv()

class SnipyBot(commands.Bot):
    def __init__(self) -> None:

        intents: Intents = Intents.default()
        allowed_mentions: AllowedMentions = AllowedMentions(
            everyone=False,
            replied_user=True,
            roles=True,
            users=True
        )
        status: Status = Status.streaming

        super().__init__(
            command_prefix=commands.when_mentioned, 
            help_command=None,
            intents=intents,
            activity=Game(name='Commands: mention me!'),
            allowed_mentions=allowed_mentions,
            owner_id=os.getenv('OWNER_ID'),
            reload=True,
            status=status,
            sync_commands_debug=True,
            test_guilds=[int(os.getenv('TEST_GUILD_ID'))]
            )
        
        self.TOKEN: str = os.getenv('TOKEN_BOT')
        self.my_extensions: Set[str, str] = {'cogs', 'slashCommands'}
        self.github_repo: str = "https://github.com/Snipy7374/SnipyBot-CodeWithVincentServer"
    
    async def on_ready(self) -> None:
        logging.info(f'Logged in as {self.user}  -  latency {self.latency}')
    
    async def start(self, *, reconnect: Optional[bool] = True) -> None:
        logging.info(f'Starting the bot at {datetime.utcnow()}')

        # This function is similar to a Setup_hook function
        # Load an setup here database connections etc...
        self.load_exts()
        await self.load_json_info()
        self.uptime_start: datetime = datetime.utcnow()
        self.add_persistent_views()

        await super().start(self.TOKEN, reconnect=reconnect)
    
    def add_persistent_views(self) -> None:
        logging.info(f"{datetime.utcnow()}:Loading persistent views")
        self.add_view(DropdownView())
        self.add_view(DropdownViewRoles())
        self.add_view(DropdownViewSystem())
        self.add_view(ButtonView())

    def load_exts(self) -> None:
        for i in self.my_extensions:
            if os.path.isdir(f'./{i}'):
                super().load_extensions(f'./{i}')
                logging.info(f'{i} extension path was loaded succesfully')
    
    async def load_json_info(self) -> None:
        json_path: Path = Path('./config.json')
        async with aiofiles.open(json_path, 'r') as f:
            content = await f.read()
        json_data: Dict[str, Any] = json.loads(content)

        self.json_info = json_data
