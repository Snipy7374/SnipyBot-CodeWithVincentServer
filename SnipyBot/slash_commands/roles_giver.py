from __future__ import annotations
from typing import TYPE_CHECKING

import disnake

from disnake import MessageInteraction
from disnake.ext import commands
from disnake.ext.commands import Context

from _logging import log_message

if TYPE_CHECKING:
    from bot import SnipyBot

__all__ = (
    "DropdownView",
)

class Dropdown(disnake.ui.Select):
    def __init__(self):
        options = [
            disnake.SelectOption(
                label="YouTube",
                description="You joined the server through YouTube",
                emoji="❤️",
            ),
            disnake.SelectOption(
                label="TikTok",
                description="You joined the server through TikTok",
                emoji="👯‍♂️",
            ),
            disnake.SelectOption(
                label="Reddit",
                description="You joined the server through Reddit",
                emoji="🌝",
            ),
            disnake.SelectOption(
                label="Other",
                description="You joined the server from other sussy platform",
                emoji="👀",
            ),
            disnake.SelectOption(
                label="Reset", description="Reset your start role", emoji="❌"
            ),
        ]

        super().__init__(
            placeholder="How did you find out about this server? (Pick one role)",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="DropdownRoleGiver",
        )

    async def callback(self, inter: MessageInteraction):
        if inter.data.values:
            if inter.data.values[0] != "Reset":
                roles = {
                    "YouTube": 939032108104572929,
                    "TikTok": 939031962952282173,
                    "Reddit": 939034123555708969,
                    "Other": 939032139691872287,
                }
                picked_role = inter.guild.get_role(roles[inter.data.values[0]])
                newbie_role = inter.guild.get_role(939024793389400106)

                add_this_shit = (picked_role, newbie_role)

                list_roles = roles.values()

                if not picked_role in inter.author.roles and not [
                    i.id for i in inter.author.roles if i.id in list_roles
                ]:
                    await inter.author.add_roles(
                        *add_this_shit,
                        reason="Picked Start role from Start-Here channel",
                        atomic=True,
                    )
                    await inter.response.send_message(
                        f"{picked_role.mention} was succesfully added to your member profile (note also {newbie_role.mention} was added to give you the access to the server)",
                        ephemeral=True,
                    )
                    log_message(
                        function_name=self.callback.__qualname__,
                        message=f"<Y>{inter.author}</> | <Y>{inter.author.id}</> interacted with \
                        {self.__class__} and picked <r>{'</>, <r>'.join(role.name for role in add_this_shit)}</> - <e>{inter.guild}</> | <e>{inter.guild.id}</>",
                    )
                else:
                    await inter.response.send_message(
                        "You already have a start role!", ephemeral=True
                    )

            elif inter.data.values[0] == "Reset":
                roles = [
                    939032108104572929,
                    939031962952282173,
                    939034123555708969,
                    939032139691872287,
                ]
                roles_obj = tuple((inter.guild.get_role(i) for i in roles)) # need to fix this shit
                try:
                    await inter.author.remove_roles(
                        *roles_obj, reason="Reset start role", atomic=True
                    )
                    await inter.response.send_message(
                        "Start roles resetted", ephemeral=True
                    )
                    log_message(
                        function_name=self.callback.__qualname__,
                        message=f"<Y>{inter.author}</> | <Y>{inter.author.id}</> interacted with \
                        {self.__class__} and unpicked <r>{'</>, <r>'.join(role.name for role in roles_obj)}</> - <e>{inter.guild}</> | <e>{inter.guild.id}</>",
                    )
                except:
                    await inter.response.send_message(
                        "Something went wrong, contact the owner of the bot (see </about:0>)",
                        ephemeral=True,
                    )


class DropdownView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())


class RoleGiver(commands.Cog):
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def create_dropdown_role_giver(self, ctx: Context):
        view = DropdownView()
        embed = disnake.Embed(
            title="Welcome to Code With Vincent!",
            description=(
            "Currently our main bot is offline!\nTo acces the server pick a role from the"
            "dropdown menù\n\nYouTube: ❤️\nTikTok: 👯‍♂️\nReddit: 🌝\nOther: 👀"
            ),
            color=disnake.Color.from_rgb(208, 255, 0),
        )
        await ctx.send(embed=embed, view=view)
        log_message(
            function_name=self.create_dropdown_role_giver.qualified_name,
            message=(
            f"<Y>{ctx.author}</> | <Y>{ctx.author.id}</> created the roles giver panel in"
            f"<e>{ctx.channel}</> | <e>{ctx.channel.id}</> channel - <e>{ctx.guild}</> | <e>{ctx.guild.id}</>"
            ),
        )


def setup(bot: SnipyBot):
    bot.add_cog(RoleGiver())
