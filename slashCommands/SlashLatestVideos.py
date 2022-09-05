import aiohttp
import json
import os
import disnake
import datetime
from disnake.ext import commands
from disnake.ext import tasks

class Menu(disnake.ui.View):
  def __init__(self, embeds):
    super().__init__(timeout=None)
    self.embeds = embeds
    self.embed_count = 0

    self.first_page.disabled = True
    self.prev_page.disabled = True

    for i, embed in enumerate(self.embeds):
      embed.set_footer(text=f"Page {i + 1} of {len(self.embeds)}")


  @disnake.ui.button(emoji="⏪", style=disnake.ButtonStyle.blurple)
  async def first_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
    self.embed_count = 0
    embed = self.embeds[self.embed_count]
    embed.set_footer(text=f"Page 1 of {len(self.embeds)}")

    self.first_page.disabled = True
    self.prev_page.disabled = True
    self.next_page.disabled = False
    self.last_page.disabled = False
    await interaction.response.edit_message(embed=embed, view=self)

  @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
  async def prev_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
    self.embed_count -= 1
    embed = self.embeds[self.embed_count]

    self.next_page.disabled = False
    self.last_page.disabled = False
    if self.embed_count == 0:
      self.first_page.disabled = True
      self.prev_page.disabled = True
    await interaction.response.edit_message(embed=embed, view=self)

  
  @disnake.ui.button(emoji="❌", style=disnake.ButtonStyle.red)
  async def remove(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
    await interaction.response.edit_message(view=None)

  @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
  async def next_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
    self.embed_count += 1
    embed = self.embeds[self.embed_count]

    self.first_page.disabled = False
    self.prev_page.disabled = False
    if self.embed_count == len(self.embeds) - 1:
      self.next_page.disabled = True
      self.last_page.disabled = True
    await interaction.response.edit_message(embed=embed, view=self)

  @disnake.ui.button(emoji="⏩", style=disnake.ButtonStyle.blurple)
  async def last_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
    self.embed_count = len(self.embeds) - 1
    embed = self.embeds[self.embed_count]

    self.first_page.disabled = False
    self.prev_page.disabled = False
    self.next_page.disabled = True
    self.last_page.disabled = True
    await interaction.response.edit_message(embed=embed, view=self)



class SlashLatestVideos(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot
    self.videos = []

  @tasks.loop(minutes=5.0)
  async def get_request(self):
    
    CHANNEL_ID = 'UCfwSZMnpzluV01vjf8ujSwQ'
    API_KEY = os.getenv('YOUTUBE_KEY')
    
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={CHANNEL_ID}&maxResults=10&order=date&type=video&key={API_KEY}'

    async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
        json_data = json.loads(await response.text())
        
        for i in json_data['items']:
          snippet = i.get('snippet')
          ids = i.get('id')
          thumb = snippet.get('thumbnails')
          high_img = thumb.get('high')
          high_img_url = high_img.get('url')

          time = snippet.get('publishedAt')
          date = datetime.datetime.fromisoformat(time[:-1]+'+00:00')
          
          embed = disnake.Embed(
            title=f"{snippet.get('title')}",
            description=f"Published at: {date.strftime('%Y-%m-%d %H:%M:%S')}\n\n{snippet.get('description')}\n[Link to video](https://www.youtube.com/watch?v={ids.get('videoId')}  '')",
            color=disnake.Color.from_rgb(208, 255, 0)
          )
          embed.set_author(
            name='YouTube', url=f"https://www.youtube.com/c/CodewithVincent"
          )
          embed.set_image(
            url=high_img_url
          )
          self.videos.append(embed)
    return json_data

  @commands.Cog.listener()
  async def on_ready(self):
    await self.get_request()
  
  @commands.slash_command(description="Send the 10 latest videos of CodeWithVincent youtune channel.")
  async def latestvideos(self, inter):
    
    await inter.response.send_message(embed=self.videos[0], view=Menu(self.videos))

      
def setup(bot):
  bot.add_cog(SlashLatestVideos(bot))