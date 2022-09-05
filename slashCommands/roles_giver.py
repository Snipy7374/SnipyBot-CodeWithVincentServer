from __future__ import annotations

import disnake
from disnake.ext import commands


from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from bot import SnipyBot


class Dropdown(disnake.ui.Select):
  def __init__(self):

    options = [
    disnake.SelectOption(
      label="YouTube", description="You joined the server through YouTube", emoji="❤️"
    ),
    disnake.SelectOption(
      label="TikTok", description="You joined the server through TikTok", emoji="👯‍♂️"
    ),
    disnake.SelectOption(
      label="Reddit", description="You joined the server through Reddit", emoji="🌝"
    ),
    disnake.SelectOption(
      label="Other", description="You joined the server from other sussy platform", emoji="👀"
    ),
    disnake.SelectOption(
      label="Reset", description="Reset your start role", emoji="❌"
    )
    ]

    super().__init__(
      placeholder="How did you find out about this server? (Pick one role)",
      min_values=1,
      max_values=1,
      options=options,
      custom_id="DropdownRoleGiver"
    )

  async def callback(self, interaction: disnake.MessageInteraction):
    if interaction.data.values[0] != "Reset":
      roles = {
        'YouTube': 939032108104572929,
        'TikTok': 939031962952282173,
        'Reddit': 939034123555708969,
        'Other': 939032139691872287
      }
      picked_role = interaction.guild.get_role(roles[interaction.data.values[0]])
      newbie_role = interaction.guild.get_role(939024793389400106)

      add_this_shit = (picked_role, newbie_role)
      
      list_roles = roles.values()
  
      if not picked_role in interaction.author.roles and not [i.id for i in interaction.author.roles if i.id in list_roles]:
        await interaction.author.add_roles(*add_this_shit, reason='Picked Start role from Start-Here channel', atomic=True)
        await interaction.response.send_message(f"{picked_role.mention} was succesfully added to your member profile (note also {newbie_role.mention} was added to give you the access to the server)", ephemeral=True)
      else:
        await interaction.response.send_message("You already have a start role!", ephemeral=True)

    elif interaction.data.values[0] == "Reset":
      roles = [939032108104572929, 939031962952282173, 939034123555708969, 939032139691872287]
      roles_obj = tuple((interaction.guild.get_role(i) for i in roles))
      try:
        await interaction.author.remove_roles(*roles_obj, reason='Reset start role', atomic=True)
        await interaction.response.send_message("Start roles resetted", ephemeral=True)
      except:
        await interaction.response.send_message("Something went wrong, contact the owner of the bot (see /about)", ephemeral=True)

class DropdownView(disnake.ui.View):
  def __init__(self):
    super().__init__(timeout=None)
    self.add_item(Dropdown())

class RoleGiver(commands.Cog):
  def __init__(self, bot: SnipyBot):
    self.bot = bot


  @commands.command()
  @commands.has_permissions(ban_members=True)
  async def create_dropdown_role_giver(self, ctx):
    view = DropdownView()
    embed = disnake.Embed(
      title="Welcome to Code With Vincent!",
      description="""Currently our main bot is offline!\nTo acces the server pick a role from the dropdown menù\n\nYouTube: ❤️\nTikTok: 👯‍♂️\nReddit: 🌝\nOther: 👀""",
      color=disnake.Color.from_rgb(208, 255, 0)
    )
    await ctx.send(embed=embed, view=view)



def setup(bot: SnipyBot):
  bot.add_cog(RoleGiver(bot))

