from __future__ import annotations
from typing import Optional, Any, TYPE_CHECKING, TypedDict

import attrs

import aiohttp
import disnake
from disnake import Embed
from disnake.ext import commands

from _logging import log_message, _logger

if TYPE_CHECKING:
    from bot import SnipyBot

__all__ = (
    "RawPackagePayload",
    "ParsedPayload",
    "PackageAuthor",
    "PackageMetadata",
    "Package",
    "flatten_dict",
)

class RawPackagePayload(TypedDict):
    info: dict[str, str]
    last_serial: int
    releases: dict[str, Any]
    urls: list[Any]
    vulnerabilities: list[str]


class ParsedPayload(TypedDict):
    info: dict[str, Any]
    author: dict[str, Any]
    package: dict[str, Any]


@attrs.define(kw_only=True, repr=True)
class PackageAuthor:
    name: str
    email: Optional[str]


@attrs.define(kw_only=True, repr=True, slots=True)
class PackageMetadata:
    name: str
    description: Optional[str]
    version: str
    url: str
    license: Optional[str]
    home_page: Optional[str]
    docs_url: Optional[str]
    summary: Optional[str]
    projects_urls: Optional[dict[str, str]]
    classifiers: Optional[list[str]]
    releases_metadata: dict[str, Any]
    vulnerabilities: Optional[list[str]]


@attrs.define(kw_only=True, repr=True)
class Package:
    author: PackageAuthor
    package: PackageMetadata


def flatten_dict(data: RawPackagePayload) -> ParsedPayload:
    parsed_payload: ParsedPayload = {}  # type: ignore # i need to fix something here big skill issue
    raw_info: dict[str, Any] = data.get("info", {})

    parsed_payload["info"] = raw_info
    parsed_payload["author"] = {
        "name": raw_info.get("author"),
        "email": raw_info.get("author_email", None),
    }
    parsed_payload["package"] = {
        "name": raw_info.get("name"),
        "description": raw_info.get("description", None),
        "version": raw_info.get("version"),
        "url": raw_info.get("package_url"),
        "license": raw_info.get("license", None),
        "home_page": raw_info.get("home_page", None),
        "docs_url": raw_info.get("docs_url", None),
        "summary": raw_info.get("summary", None),
        "projects_urls": raw_info.get("project_urls", None),
        "classifiers": raw_info.get("classifiers", None),
        "releases_metadata": data.get("releases", {}),
        "vulnerabilities": data.get("vulnerabilities", None),
    }
    return parsed_payload


class PackagesSearcher(commands.Cog):
    BASE_URL: str = "https://pypi.org/pypi/{package}/json"
    PYPI_ICON: str = "https://cdn.discordapp.com/emojis/766274397257334814.png"

    def __init__(self, bot: SnipyBot) -> None:
        self.bot = bot

    @commands.slash_command()
    async def packages(self, inter) -> None:
        return

    async def pypi_request(self, package_name: str) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.BASE_URL.format(package=package_name)
            ) as response:
                response_content = await response.json()
                if response.status == 404:
                    return {"Error": f"Couldn't find the package {package_name}"}

                elif (
                    response.status == 200
                    and response.content_type == "application/json"
                ):
                    _logger.debug(f"Request made <g>successfully</>, obtained <e>{response_content}</>")
                    return response_content

                else:
                    _logger.error(
                        f"<r>Something went wrong while searching \
                        the package '{package_name}' original response={response_content}</>",
                    )
                    return {"Error": f"Something went wrong searching {package_name}"}

    @packages.sub_command(description="Retrieve information about packages")
    async def search(self, inter, package_name: str) -> None:
        response = await self.pypi_request(package_name)
        raw_payload: RawPackagePayload = RawPackagePayload(**response)
        flatten_payload = flatten_dict(raw_payload)
        package_author = PackageAuthor(**(flatten_payload.get("author")))
        package = PackageMetadata(**(flatten_payload.get("package")))

        if isinstance(response, dict) and "Error" not in response.keys():
            package_obj = Package(author=package_author, package=package)

            embed = Embed(
                title=package_obj.package.name,
                url=package_obj.package.url,
                description=package_obj.package.summary,
                color=disnake.Color.from_rgb(208, 255, 0),
            )
            embed.add_field(
                name="Author",
                value=f"{package_obj.author.name} - {package_obj.author.email}",
                inline=False,
            )
            if (
                package_obj.package.description
                and len(package_obj.package.description) > 1024
            ):
                package_obj.package.description = (
                    package_obj.package.description[:1021] + "..."
                )
            embed.add_field(
                name="Description", value=package_obj.package.description, inline=False
            )
            embed.add_field(
                name="Classifiers",
                value=", ".join(package_obj.package.classifiers or []),
            )
            embed.add_field(
                name="Other info",
                value=f"**[{package_obj.package.name} v{package_obj.package.version}]({package_obj.package.url} '')** - {package_obj.package.license}",
                inline=False,
            )
            releases = [i for i in (package_obj.package.releases_metadata).keys()]
            releases = releases[: len(releases) - 15 : -1]
            embed.add_field(
                name="Releases (latest 15 - from latest to oldest)",
                value=", ".join(releases),
                inline=False,
            )
            embed.set_thumbnail(url=self.PYPI_ICON)
            await inter.response.send_message(embed=embed)
            log_message(
                function_name=self.search.qualified_name,
                message=f"<Y>{inter.author}</> | <Y>{inter.author.id}</> searched the <r>'{package_name}'</> package \
                <e>{inter.guild}</> | <e>{inter.guild.id}</>"
            )

        else:
            embed = Embed(
                title=package_name,
                description=response,
                color=disnake.Color.from_rgb(210, 43, 43),
            )

            await inter.response.send_message(embed=embed, delete_after=10.0)
            _logger.error(
                f"<r>Something went wrong while executing {self.search.qualified_name} \
                response={response}</>"
            )


def setup(bot: SnipyBot):
    bot.add_cog(PackagesSearcher(bot))
