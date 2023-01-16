import discord
import json


from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from helpers import checks


class Level(commands.Cog, name="level"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="rank",
        descrption="본인의 레벨과 경험치를 확인합니다."
    )
async def setup(bot):
    await bot.add_cog(Level(bot))
