from __future__ import annotations
from typing import TYPE_CHECKING

import disnake

from disnake import MessageInteraction
from disnake.ext import commands
from disnake.ext.commands import Context

from _logging import _logger

if TYPE_CHECKING:
    from bot import SnipyBot

__all__ = (
    "ButtonView",
    "DropdownViewSystem",
)

class Dropdown(disnake.ui.Select):
    def __init__(self):
        options = [
            disnake.SelectOption(
                label="Linux", description="The real programmer", emoji="🐧"
            ),
            disnake.SelectOption(label="Windows", description="Ayo bro", emoji="💻"),
            disnake.SelectOption(label="MacOS", description="Sugar daddy", emoji="🍎"),
        ]

        super().__init__(
            placeholder="Select your System",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="SystemGiver",
        )

    async def callback(self, inter: MessageInteraction):
        roles = {
            "Linux": 943561294575972383,
            "Windows": 943561381930758144,
            "MacOS": 943561412792438845,
        }

        picked_roles = [inter.guild.get_role(roles[i]) for i in inter.data.values]
        unpicked_roles = [
            inter.guild.get_role(roles[i])
            for i in roles.keys()
            if i not in inter.data.values
        ]

        await inter.author.add_roles(
            *picked_roles,
            reason="Picked system roles from Get-Roles channel",
            atomic=True,
        )
        _logger.info(
            f"{inter.author} | {inter.author.id} | picked the following roles {', '.join(role.name for role in picked_roles)} from {inter.guild} {inter.channel.name} | {inter.channel.id}"
        )
        await inter.author.remove_roles(
            *unpicked_roles,
            reason="Unpicked system roles from Get-Roles channel",
            atomic=True,
        )
        _logger.info(
            f"{inter.author} | {inter.author.id} | unpicked the following roles {', '.join(role.name for role in unpicked_roles)} from {inter.guild} {inter.channel.name} | {inter.channel.id}"
        )
        await inter.send(
            f"You have now the following system roles: {', '.join([i.mention for i in picked_roles])}",
            ephemeral=True,
        )


class ButtonCls(disnake.ui.Button):
    def __init__(self):
        super().__init__(
            custom_id="QuestionGiver",
            label="Get question role",
            emoji="❓",
            style=disnake.ButtonStyle.danger,
        )
        self.question_role_id = 939044358903177217
        self.question_channel_id = 1014154045268709419

    async def callback(self, inter: MessageInteraction):
        question_role = inter.guild.get_role(self.question_role_id)

        if question_role in inter.author.roles:
            await inter.response.send_message(
                f"You already have the role {question_role.mention} go to <#{self.question_channel_id}> and ask for help!",
                ephemeral=True,
            )

        else:
            await inter.author.add_roles(
                question_role,
                reason="Adding Can I ask a question role from Get-Roles channel",
            )
            _logger.info(
                f"<Y>{inter.author}</> | <Y>{inter.author.id}</> picked the {question_role.name} role form {inter.guild} {inter.channel.name} | {inter.channel.id}"
            )
            await inter.response.send_message(
                f"{question_role.mention} was successfully added to your member profile, go to <#{self.question_channel_id}> and ask for help!",
                ephemeral=True,
            )


class ButtonView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ButtonCls())


class DropdownViewSystem(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())


class SystemGiver(commands.Cog):
    @commands.command()
    @commands.is_owner()
    async def system_giver(self, ctx: Context):
        view = DropdownViewSystem()
        embed = disnake.Embed(
            title="System",
            description="> 🐧 Linux\n> 💻 Windows\n> 🍎MacOS",
            color=disnake.Color.from_rgb(208, 255, 0),
        )
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.is_owner()
    async def question_giver(self, ctx: Context):
        view = ButtonView()
        embed = disnake.Embed(
            title="Can someone help me?",
            description="To get access to the questions channel, please press the button below!",
            color=disnake.Color.from_rgb(208, 255, 0),
        )
        await ctx.send(embed=embed, view=view)


def setup(bot: SnipyBot):
    bot.add_cog(SystemGiver())
