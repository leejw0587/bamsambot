import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, db_manager


class Shop(commands.Cog, name="shop"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="shop",
        description="상점 관련 기능을 제공합니다."
    )
    async def shop(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                title="Error!",
                description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`list` - 상점에 등록된 아이템을 확인합니다.\n`buy` - 등록된 아이템을 구매합니다.\n`add` - 상점에 아이템을 추가합니다.\n`remove` - 상점에서 아이템을 제거합니다.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @shop.command(
        name="list",
        description="상점에 등록된 아이템을 확인합니다.",
    )
    async def shop_list(self, context: Context) -> None:
