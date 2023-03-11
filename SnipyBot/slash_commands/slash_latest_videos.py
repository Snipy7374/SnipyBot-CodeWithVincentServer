from __future__ import annotations
from typing import TYPE_CHECKING

import json
import datetime
from os import environ

import aiohttp
import disnake
from disnake.ext import commands, tasks

from _logging import log_message, _logger

if TYPE_CHECKING:
    from bot import SnipyBot

__all__ = (
    "Menu",
)

class Menu(disnake.ui.View):
    def __init__(self, embeds, interaction):
        super().__init__(timeout=360)
        self.embeds = embeds
        self.embed_count = 0

        self.first_page.disabled = True
        self.prev_page.disabled = True

        self.original_interaction: disnake.AppCmdInter = interaction

        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Page {i + 1} of {len(self.embeds)}")

    async def on_timeout(self) -> None:
        await super().on_timeout()
        if embeds := (await self.original_interaction.original_message()).embeds:
            for embed in embeds:
                embed.set_footer(text=f"Command timed out!")
        await self.original_interaction.edit_original_response(embeds=embeds)

    @disnake.ui.button(emoji="⏪", style=disnake.ButtonStyle.blurple)
    async def first_page(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.embed_count = 0
        embed = self.embeds[self.embed_count]
        embed.set_footer(text=f"Page 1 of {len(self.embeds)}")

        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = False
        self.last_page.disabled = False
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.embed_count -= 1
        embed = self.embeds[self.embed_count]

        self.next_page.disabled = False
        self.last_page.disabled = False
        if self.embed_count == 0:
            self.first_page.disabled = True
            self.prev_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="❌", style=disnake.ButtonStyle.red)
    async def remove(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.response.edit_message(view=None)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.embed_count += 1
        embed = self.embeds[self.embed_count]

        self.first_page.disabled = False
        self.prev_page.disabled = False
        if self.embed_count == len(self.embeds) - 1:
            self.next_page.disabled = True
            self.last_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(emoji="⏩", style=disnake.ButtonStyle.blurple)
    async def last_page(
        self, _: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        self.embed_count = len(self.embeds) - 1
        embed = self.embeds[self.embed_count]

        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.next_page.disabled = True
        self.last_page.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)


class SlashLatestVideos(commands.Cog):
    def __init__(self, bot: SnipyBot):
        self.bot = bot
        self.videos = []

    @tasks.loop(minutes=5.0)
    async def get_request(self):
        BASE_URL = "https://www.googleapis.com/youtube/v3/"
        SEARCH_ENDPOINT = "search?part=snippet&channelId="
        CHANNEL_ID = "UCfwSZMnpzluV01vjf8ujSwQ"
        FILTERS = "&maxResults=10&order=date&type=video"
        API_KEY = environ["YOUTUBE_KEY"]

        url = f"{BASE_URL}{SEARCH_ENDPOINT}{CHANNEL_ID}{FILTERS}&key={API_KEY}"

        log_message(
            function_name="get_request",
            message=f"Making request to <b><e>{BASE_URL}{SEARCH_ENDPOINT}{CHANNEL_ID}{FILTERS}</e></b>",
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                json_data = json.loads(await response.text())

                for i in json_data["items"]:
                    snippet = i.get("snippet")
                    ids = i.get("id")
                    thumb = snippet.get("thumbnails")
                    high_img = thumb.get("high")
                    high_img_url = high_img.get("url")

                    time = snippet.get("publishedAt")
                    date = datetime.datetime.fromisoformat(time[:-1] + "+00:00")

                    embed = disnake.Embed(
                        title=f"{snippet.get('title')}",
                        description=f"Published at: {date.strftime('%Y-%m-%d %H:%M:%S')}\n\n{snippet.get('description')}\n[Link to video](https://www.youtube.com/watch?v={ids.get('videoId')}  '')",
                        color=disnake.Color.from_rgb(208, 255, 0),
                    )
                    embed.set_author(
                        name="YouTube", url="https://www.youtube.com/c/CodewithVincent"
                    )
                    embed.set_image(url=high_img_url)
                    self.videos.append(embed)
        _logger.debug(
            f"Incoming request response {json_data}"
        )  # i can't use my custom logger here cause the dict raise problems with the
        # tag parser, i could monkeypatch it too in a future version
        return json_data

    @commands.Cog.listener()
    async def on_ready(self):
        await self.get_request()

    @commands.slash_command(
        description="Send the 10 latest videos of CodeWithVincent youtune channel."
    )
    async def latestvideos(self, inter):

        await inter.response.send_message(
            embed=self.videos[0], view=Menu(self.videos, interaction=inter)
        )
        inter.latest_videos_embeds = self.videos


def setup(bot: SnipyBot):
    bot.add_cog(SlashLatestVideos(bot))
