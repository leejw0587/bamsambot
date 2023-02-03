from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="testcommand",
        description="This is a testing command that does nothing.",
    )
    @checks.not_blacklisted()
    @checks.is_owner()
    async def testcommand(self, context: Context):
        pass


async def setup(bot):
    await bot.add_cog(Template(bot))
