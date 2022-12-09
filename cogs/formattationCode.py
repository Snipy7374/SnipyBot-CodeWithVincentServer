from __future__ import annotations

import disnake
from disnake.ext import commands

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from bot import SnipyBot


class formattationCode(commands.Cog):
  def __init__(self, bot: SnipyBot):
    self.bot = bot

  @commands.command(aliases=['format', 'codeformat', 'cf'])
  async def code(self, ctx):
    embed = disnake.Embed(
      title='Discord code format',
      description="To be able to format a script on Discord follow the instructions below.",
      color=disnake.Color.from_rgb(208, 255, 0),
    )
    embed.add_field(
      name="Result",
      value="```py\nprint('Hello World!')\n```",
      inline=False
    )
    embed.add_field(
      name="Syntax",
      value="The `<lang>` parameter must be replaced by the code of your script (example: py)\n\```<lang>\nyour code here...\n```"
    )
    embed.add_field(
      name='Docs',
      value="You can find more information on **[Discord Markdown Guide](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline- '')**.",
      inline=False
    )
    await ctx.reply(embed=embed)
 
def setup(bot: SnipyBot):
  bot.add_cog(formattationCode(bot))