import discord
import json
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, db_manager


class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command(
    #     name="sync",
    #     description="Synchonizes the slash commands.",
    # )
    # @app_commands.describe(scope="The scope of the sync. Can be `global` or `guild`")
    # @checks.is_owner()
    # async def sync(self, context: Context, scope: str) -> None:
    #     """
    #     Synchonizes the slash commands.

    #     :param context: The command context.
    #     :param scope: The scope of the sync. Can be `global` or `guild`.
    #     """

    #     if scope == "global":
    #         await context.bot.tree.sync()
    #         embed = discord.Embed(
    #             title="Slash Commands Sync",
    #             description="Slash commands have been globally synchronized.",
    #             color=0x9C84EF
    #         )
    #         await context.send(embed=embed)
    #         return
    #     elif scope == "guild":
    #         context.bot.tree.copy_global_to(guild=context.guild)
    #         await context.bot.tree.sync(guild=context.guild)
    #         embed = discord.Embed(
    #             title="Slash Commands Sync",
    #             description="Slash commands have been synchronized in this guild.",
    #             color=0x9C84EF
    #         )
    #         await context.send(embed=embed)
    #         return
    #     embed = discord.Embed(
    #         title="Invalid Scope",
    #         description="The scope must be `global` or `guild`.",
    #         color=0xE02B2B
    #     )
    #     await context.send(embed=embed)

    # @commands.command(
    #     name="unsync",
    #     description="Unsynchonizes the slash commands.",
    # )
    # @app_commands.describe(scope="The scope of the sync. Can be `global`, `current_guild` or `guild`")
    # @checks.is_owner()
    # async def unsync(self, context: Context, scope: str) -> None:
    #     """
    #     Unsynchonizes the slash commands.

    #     :param context: The command context.
    #     :param scope: The scope of the sync. Can be `global`, `current_guild` or `guild`.
    #     """

    #     if scope == "global":
    #         context.bot.tree.clear_commands(guild=None)
    #         await context.bot.tree.sync()
    #         embed = discord.Embed(
    #             title="Slash Commands Unsync",
    #             description="Slash commands have been globally unsynchronized.",
    #             color=0x9C84EF
    #         )
    #         await context.send(embed=embed)
    #         return
    #     elif scope == "guild":
    #         context.bot.tree.clear_commands(guild=context.guild)
    #         await context.bot.tree.sync(guild=context.guild)
    #         embed = discord.Embed(
    #             title="Slash Commands Unsync",
    #             description="Slash commands have been unsynchronized in this guild.",
    #             color=0x9C84EF
    #         )
    #         await context.send(embed=embed)
    #         return
    #     embed = discord.Embed(
    #         title="Invalid Scope",
    #         description="The scope must be `global` or `guild`.",
    #         color=0xE02B2B
    #     )
    #     await context.send(embed=embed)

    @commands.hybrid_command(
        name="load",
        description="cog를 로드합니다. (창조자 전용)",
    )
    @app_commands.describe(cog="로드할 cog 이름")
    @checks.is_owner()
    async def load(self, context: Context, cog: str) -> None:
        """
        The bot will load the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to load.
        """
        try:
            await self.bot.load_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                title="Error!",
                description=f"Could not load the `{cog}` cog.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            title="Load",
            description=f"Successfully loaded the `{cog}` cog.",
            color=0x9C84EF
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="unload",
        description="cog를 언로드합니다. (창조자 전용)",
    )
    @app_commands.describe(cog="언로드할 cog 이름")
    @checks.is_owner()
    async def unload(self, context: Context, cog: str) -> None:
        """
        The bot will unload the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to unload.
        """
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                title="Error!",
                description=f"Could not unload the `{cog}` cog.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            title="Unload",
            description=f"Successfully unloaded the `{cog}` cog.",
            color=0x9C84EF
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="reload",
        description="cog를 리로드합니다. (창조자 전용)",
    )
    @app_commands.describe(cog="리로드할 cog 이름")
    @checks.is_owner()
    async def reload(self, context: Context, cog: str) -> None:
        """
        The bot will reload the given cog.

        :param context: The hybrid command context.
        :param cog: The name of the cog to reload.
        """
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                title="Error!",
                description=f"Could not reload the `{cog}` cog.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            title="Reload",
            description=f"Successfully reloaded the `{cog}` cog.",
            color=0x9C84EF
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="shutdown",
        description="봇을 강제종료합니다. (창조자 전용)",
    )
    @checks.is_owner()
    async def shutdown(self, context: Context) -> None:
        """
        Shuts down the bot.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description="Shutting down. Bye! :wave:",
            color=0x9C84EF
        )
        await context.send(embed=embed)
        await self.bot.close()

    @commands.hybrid_command(
        name="say",
        description="입력한 메시지를 봇이 대신 말해줍니다. (창조자 전용)",
    )
    @app_commands.describe(message="보낼 메시지")
    @checks.is_owner()
    async def say(self, context: Context, *, message: str) -> None:
        """
        The bot will say anything you want.

        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        await context.send(message)

    @commands.hybrid_command(
        name="embed",
        description="봇이 embed 형태로 메시지를 보내줍니다. (창조자 전용)",
    )
    @app_commands.describe(message="보낼 메시지")
    @checks.is_owner()
    async def embed(self, context: Context, *, message: str) -> None:
        """
        The bot will say anything you want, but using embeds.

        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        embed = discord.Embed(
            description=message,
            color=0x9C84EF
        )
        await context.send(embed=embed)

    # @commands.hybrid_group(
    #     name="blacklist",
    #     description="블랙리스트를 관리합니다.",
    # )
    # @checks.is_owner()
    # async def blacklist(self, context: Context) -> None:
    #     """
    #     Lets you add or remove a user from not being able to use the bot.

    #     :param context: The hybrid command context.
    #     """
    #     if context.invoked_subcommand is None:
    #         embed = discord.Embed(
    #             title="Blacklist",
    #             description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`add` - 유저를 블랙리스트에 추가합니다.\n`remove` - 유저를 블랙리스트에서 제거합니다.",
    #             color=0xE02B2B
    #         )
    #         await context.send(embed=embed)

    # @blacklist.command(
    #     base="blacklist",
    #     name="add",
    #     description="유저가 봇을 사용할 수 없도록 합니다.",
    # )
    # @app_commands.describe(user="The user that should be added to the blacklist")
    # @checks.is_owner()
    # async def blacklist_add(self, context: Context, user: discord.User) -> None:
    #     """
    #     Lets you add a user from not being able to use the bot.

    #     :param context: The hybrid command context.
    #     :param user: The user that should be added to the blacklist.
    #     """
    #     user_id = user.id
    #     if await db_manager.is_blacklisted(user_id):
    #         embed = discord.Embed(
    #             title="Error!",
    #             description=f"**{user.name}** is not in the blacklist.",
    #             color=0xE02B2B
    #         )
    #         await context.send(embed=embed)
    #         return
    #     total = await db_manager.add_user_to_blacklist(user_id)
    #     embed = discord.Embed(
    #         title="User Blacklisted",
    #         description=f"**{user.name}** has been successfully added to the blacklist",
    #         color=0x9C84EF
    #     )
    #     embed.set_footer(
    #         text=f"There are now {total} {'user' if total == 1 else 'users'} in the blacklist"
    #     )
    #     await context.send(embed=embed)

    # @blacklist.command(
    #     base="blacklist",
    #     name="remove",
    #     description="Lets you remove a user from not being able to use the bot.",
    # )
    # @app_commands.describe(user="The user that should be removed from the blacklist.")
    # @checks.is_owner()
    # async def blacklist_remove(self, context: Context, user: discord.User) -> None:
    #     """
    #     Lets you remove a user from not being able to use the bot.

    #     :param context: The hybrid command context.
    #     :param user: The user that should be removed from the blacklist.
    #     """
    #     user_id = user.id
    #     if not await db_manager.is_blacklisted(user_id):
    #         embed = discord.Embed(
    #             title="Error!",
    #             description=f"**{user.name}** is already in the blacklist.",
    #             color=0xE02B2B
    #         )
    #         await context.send(embed=embed)
    #         return
    #     total = await db_manager.remove_user_from_blacklist(user_id)
    #     embed = discord.Embed(
    #         title="User removed from blacklist",
    #         description=f"**{user.name}** has been successfully removed from the blacklist",
    #         color=0x9C84EF
    #     )
    #     embed.set_footer(
    #         text=f"There are now {total} {'user' if total == 1 else 'users'} in the blacklist"
    #     )
    #     await context.send(embed=embed)
    @commands.hybrid_command(
        name="initialize",
        description="initialize all userdata (창조자 전용)",
    )
    @checks.is_owner()
    async def initialize(self, context: Context) -> None:
        with open("database/userdata.json", encoding="UTF-8") as file:
            userdata = json.load(file)
        for guild in self.bot.guilds:
            for member in guild.members:
                newUser = {
                    str(member.id): {
                        "username": str(member),
                        "userid": str(member.id),
                        "peridot": 1000,
                        "token": 0,
                        "xp": 0,
                        "level": 0,
                        "attendance": 0,
                        "last_attendance": ""
                    }
                }
                userdata.update(newUser)
                with open("database/userdata.json", 'w', encoding="UTF-8") as file:
                    json.dump(userdata, file, indent="\t", ensure_ascii=False)

        await context.send("Initialized `userdata.json`")


async def setup(bot):
    await bot.add_cog(Owner(bot))
