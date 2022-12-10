from __future__ import annotations
from typing import TYPE_CHECKING

import disnake
from disnake.ext import commands

if TYPE_CHECKING:
    from bot import SnipyBot


class Dropdown(disnake.ui.Select):
    def __init__(self) -> None:
        options = [
            disnake.SelectOption(
                label="Python", description="You're a Python brogrammer", emoji="🔵"
            ),
            disnake.SelectOption(
                label="Html/Css", description="You're a typical Web Dev", emoji="🟠"
            ),
            disnake.SelectOption(
                label="JavaScript", description="How can you use a language that doesn't support 1.7976931348623157e+309", emoji="🟡"
            ),
            disnake.SelectOption(
                label="C/C++/C#", description="You're the final brogrammer", emoji="🟢"
            ),
            disnake.SelectOption(
                label="Java", description="An unofficial Python version", emoji="🔴"
            ),
            disnake.SelectOption(
                label="SQL/NoSQL", description="You're most likely an SQL injecter", emoji="🟤"
            ),
            disnake.SelectOption(
                label="Assembly", description="msg db 'Hello, World!', 0x0d, 0x0a, '$' ;", emoji="🟣"
            ),
        ]

        super().__init__(
            placeholder="Select your Coding languages",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="RolesGiver"
        )

    async def callback(self, inter):
        roles = {
            "Python": 943560724809150505,
            "Html/Css": 943560917361258536,
            "JavaScript": 943560788185059339,
            "C/C++/C#": 943561036567576636,
            "Java": 943561127449726977,
            "SQL/NoSQL": 943561155551559770,
            "Assembly": 943561249801773096,
        }
        picked_roles = [inter.guild.get_role(roles[inter.data.values[i]]) for i in range(len(inter.data.values))]
        unpicked_roles = [inter.guild.get_role(roles[i]) for i in roles.keys() if i not in inter.data.values]


        await inter.author.add_roles(*picked_roles, reason='Picked Coding roles from Get-Roles channel', atomic=True)
        await inter.author.remove_roles(*unpicked_roles, reason="Unpicked Coding roles from Get-Roles channel")
        out_roles = [i.mention for i in picked_roles]
        await inter.response.send_message(f"You have now the following coding languages: {', '.join(out_roles)}", ephemeral=True)


class DropdownViewRoles(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())


class Test(commands.Cog):
    def __init__(self, bot: SnipyBot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def create_roles(self, ctx):
        view = DropdownViewRoles()
        embed = disnake.Embed(
        title="Extra roles",
        description="""**Coding Languages**\n\n> 🔵 Python\n> 🟠 Html/CSS\n> 🟡 JavaScript\n> 🟢 C/C++/C#\n> 🔴 Java\n> 🟤 SQL/NoSQL\n> 🟣 Assembly""",
        color=disnake.Color.from_rgb(208, 255, 0)
        )
        await ctx.send(embed=embed, view=view)


def setup(bot: SnipyBot):
    bot.add_cog(Test(bot))