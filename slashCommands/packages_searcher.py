from __future__ import annotations

from disnake import Embed
from disnake.ext import commands
import disnake

from typing import (
  Optional,
  Union,
  Dict,
  Any,
  List,
  TYPE_CHECKING
)

import aiohttp

if TYPE_CHECKING:
  from bot import SnipyBot

class Package:
  author: str
  author_email: Optional[str]

  classifiers: Optional[List[str]]
  description: Optional[str]
  docs_url: Optional[str]
  home_page: Optional[str]
  license: str

  package_name: str
  package_url: str
  project_urls: Optional[Dict[str, str]]
  summary: str
  version: str

  releases: Optional[Dict[str, Union[List[str], Any]]]
  vulnerabilities: Optional[List[Any]]

  
  def __init__(self, *, data: Dict[str, Any]) -> None:
    self.data = data

    __info_dict = self.data.get("info", {})
    self.author = __info_dict.get("author", None)
    self.author_email = __info_dict.get("author_email")
    self.classifiers = __info_dict.get("classifiers", None)
    self.description = __info_dict.get("descriptions", None)
    self.docs_url = __info_dict.get("docs_url", None)
    self.home_page = __info_dict.get("home_page", None)
    self.license = __info_dict.get("license", None)
    self.package_name = __info_dict.get("name", None)
    self.package_url = __info_dict.get("package_url", None)
    self.project_urls = __info_dict.get("project_urls", None)
    self.summary = __info_dict.get("summary", None)
    self.version = __info_dict.get("version", None)

    __info_dict_releases = self.data.get("releases", None)
    self.releases = __info_dict_releases.keys() if __info_dict_releases else None

    self.vulnerabilities = self.data.get("vulnerabilities", None)

  def __str__(self) -> str:
    return f"<Package author={self.author}, author_email={self.author_email}, classifiers={self.classifiers}, description={self.description}, docs_url={self.docs_url}, home_page={self.home_page}, license={self.license}, package_name={self.package_name}, package_url={self.package_url}, project_urls={self.project_urls}, summary={self.summary}, version={self.version}, version={self.version}, releases={self.releases}, vulnerabilities={self.vulnerabilities}>"
  


class PackagesSearcher(commands.Cog):
  BASE_URL: str = "https://pypi.org/pypi/{package}/json"
  PYPI_ICON: str = "https://cdn.discordapp.com/emojis/766274397257334814.png"
  
  def __init__(self, bot: SnipyBot) -> None:
    self.bot = bot


  @commands.slash_command()
  async def packages(self, inter) -> None:
    return

  
  async def pypi_request(self, package_name: str) -> Union[Dict[str, Any], str]:
    async with aiohttp.ClientSession() as session:
      async with session.get(self.BASE_URL.format(package=package_name)) as response:

        if response.status == 404:
          return f"Couldn't find the package {package_name}"
          
        elif response.status == 200 and response.content_type == "application/json":
          return await response.json()
        
        else:
          return f"Something went wrong searching {package_name}"


  @packages.sub_command(description="Retrieve information about packages")
  async def search(
    self, 
    inter,
    package_name: str
  ) -> None:

    response = await self.pypi_request(package_name)
    if isinstance(response, dict):
      package_obj = Package(data=response)

      embed = Embed(
      title=package_obj.package_name,
      url=package_obj.package_url,
      description=package_obj.summary,
      color=disnake.Color.from_rgb(208, 255, 0)
      )
      embed.add_field(
        name="Author",
        value=f"{package_obj.author} - {package_obj.author_email}",
        inline=False
      )
      embed.add_field(
        name="Description",
        value=package_obj.description,
        inline=False
      )
      embed.add_field(
        name="Classifiers",
        value=', '.join(package_obj.classifiers)
      )
      embed.add_field(
        name="Other info",
        value=f"**[{package_obj.package_name} v{package_obj.version}]({package_obj.package_url} '')** - {package_obj.license}",
        inline=False
      )
      releases = [i for i in package_obj.releases]
      releases = releases[:len(releases)-15:-1]
      embed.add_field(
        name="Releases (latest 15 - from latest to oldest)",
        value=', '.join(releases),
        inline=False
      )
      embed.set_thumbnail(
        url=self.PYPI_ICON
      )
      await inter.response.send_message(embed=embed)
    
    else:
      embed = Embed(
        title=package_name,
        description=response,
        color=disnake.Color.from_rgb(210, 43, 43)
      )

      await inter.response.send_message(embed=embed, delete_after=10.0)
    


def setup(bot: SnipyBot):
  bot.add_cog(PackagesSearcher(bot))