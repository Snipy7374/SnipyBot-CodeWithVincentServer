import asyncio
from disnake.ext import commands

from bot import SnipyBot

#from keep_alive import keep_alive

bot = SnipyBot()

@bot.command()
@commands.is_owner()
async def load(ctx, folder: str, extension: str) -> None:
  if folder not in bot.my_extensions:
    await ctx.reply(f"{folder} is not a valid folder!", delete_after=10)
    await asyncio.sleep(10)
    await ctx.message.delete()
  else:
    try:
      bot.load_extension(f"{folder}.{extension}")
      await ctx.reply(f"{folder}.{extension} successfully loaded!", delete_after=10)
      await ctx.message.delete()
    except Exception as error:
      if isinstance(error, commands.ExtensionNotFound):
        await ctx.reply(f"{extension} could not be imported!", delete_after=10)
      elif isinstance(error, commands.ExtensionAlreadyLoaded):
        await ctx.reply(f"{extension} is already loaded! (unload or reload it)", delete_after=10)
      elif isinstance(error, commands.NoEntryPointError):
        await ctx.reply(f"{extension} doesn't have a setup function!", delete_after=10)
      elif isinstance(error, commands.ExtensionFailed):
        await ctx.reply(f"{extension} had an execution error!", delete_after=10)
      else:
        await ctx.reply("An unknown error has occurred", delete_after=10)
      await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def unload(ctx, folder: str, extension: str) -> None:
  if folder not in bot.my_extensions:
    await ctx.reply(f"{folder} is not a valid folder!", delete_after=10)
  else:
    try:
      bot.unload_extension(f"{folder}.{extension}")
      await ctx.reply(f"{folder}.{extension} successfully unloaded!", delete_after=10)
      await ctx.message.delete()
    except Exception as error:
      if isinstance(error, commands.ExtensionNotFound):
        await ctx.reply(f"{extension} could not be resolved!", delete_after=10)
      elif isinstance(error, commands.ExtensionNotLoaded):
        await ctx.reply(f"{extension} is not loaded!", delete_after=10)
      else:
        await ctx.reply("An unknown error has occurred", delete_after=10)
      await ctx.message.delete()

#keep_alive()
bot.run()