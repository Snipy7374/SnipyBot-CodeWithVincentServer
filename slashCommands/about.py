from __future__ import annotations

import disnake
from disnake.ext import commands
import sys
import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from bot import SnipyBot

class AboutBot(commands.Cog):
  def __init__(self, bot: SnipyBot):
    self.bot = bot
    self.language, self.version = ("Python", (sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    self.library_version = disnake.version_info
    self.library_PEP = disnake.__version__
    

  @commands.slash_command()
  async def about(self, inter):

    embed = disnake.Embed(
      title='Info',
      color=disnake.Color.from_rgb(208, 255, 0)
    )
    embed.add_field(
      name="Owner",
      value=f"<@{self.bot.owner_id}>",
      inline=False
    )
    embed.add_field(
      name="Source code",
      value=self.bot.github_repo,
      inline=False
    )
    embed.add_field(
      name="Language & version",
      value=f"`{self.language}`  -  `{'.'.join(str(i) for i in self.version)}`",
      inline=False
    )
    embed.add_field(
      name="Api library",
      value=f"`Disnake`  -  `{'.'.join(str(i) for i in self.library_version)}` (`{self.library_PEP}`)",
      inline=False
    )
    embed.add_field(
      name='Uptime since',
      value=f'{datetime.datetime.utcnow() - self.bot.uptime_start}'
    )
    await inter.response.send_message(embed=embed)


def setup(bot: SnipyBot):
  bot.add_cog(AboutBot(bot))
    