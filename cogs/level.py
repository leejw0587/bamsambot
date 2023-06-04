import discord
import json
import random

from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from helpers import checks, log, embeds

_MAXXP = 10
_MINXP = 1


class Level(commands.Cog, name="level"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.content.startswith("/"):
            if not message.author.bot:
                with open("database/userdata.json", encoding="utf-8") as file:
                    userdata = json.load(file)

                if str(message.author.id) in userdata:
                    xp = userdata[str(message.author.id)]["xp"]
                    level = userdata[str(message.author.id)]["level"]

                    increased_xp = xp + random.randint(_MINXP, _MAXXP)
                    new_level = int(increased_xp/100)

                    userdata[str(message.author.id)]["xp"] = increased_xp

                    with open("database/userdata.json", 'w', encoding="utf-8") as file:
                        json.dump(userdata, file, indent="\t",
                                  ensure_ascii=False)

                    if new_level > level:
                        await message.channel.send(f":tada: **{message.author.mention}님이 레벨업 하였습니다! [ 현재 레벨: {new_level} ]** :tada:")
                        userdata[str(message.author.id)]["level"] = new_level
                        userdata[str(message.author.id)]["xp"] = 0

                        with open("database/userdata.json", 'w', encoding="utf-8") as file:
                            json.dump(userdata, file, indent="\t",
                                      ensure_ascii=False)

    @commands.hybrid_command(
        name="leaderboard",
        description="레벨 순위를 확인합니다."
    )
    async def leaderboard(self, context: Context) -> None:
        await context.defer()
        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)

        lim = 10

        lb = {}
        total_xp = []

        for uid in userdata:
            xp = int(userdata[str(uid)]["xp"]) + \
                (int(userdata[str(uid)]["level"] * 100))

            lb[xp] = f"{uid};{userdata[str(uid)]['level']};{userdata[str(uid)]['xp']}"
            total_xp.append(xp)

        total_xp = sorted(total_xp, reverse=True)
        index = 1

        embed = discord.Embed(
            title="Bamsam Leaderboard",
            color=discord.Color.blurple()
        )

        for amt in total_xp:
            id_ = int(str(lb[amt]).split(";")[0])
            level = int(str(lb[amt]).split(";")[1])
            xp = int(str(lb[amt]).split(";")[2])

            member = await self.bot.fetch_user(id_)

            if member is not None:
                name = member.name
                embed.add_field(name=f"{index}. {name}",
                                value=f"**Level: {level} | XP: {xp}**",
                                inline=False)

            if index == lim:
                break
            else:
                index += 1

        await context.send(embed=embed)

    @commands.hybrid_group(
        name="level",
        description="레벨 관련 기능을 제공합니다. (창조자 전용)"
    )
    async def level(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                title="Error!",
                description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`set` - 유저의 레벨을 설정합니다",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @ level.command(
        name="set",
        description="유저의 레벨을 설정합니다. (창조자 전용)",
    )
    @ app_commands.describe(user="대상 유저", level="설정할 레벨")
    @ checks.is_owner()
    async def level_set(self, context: Context, user: discord.User, level: int):
        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)

        if str(user.id) not in userdata:
            embed = discord.Embed(
                title="Error!",
                description="유저를 찾을 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

        else:
            userdata[str(user.id)]["level"] = level
            with open("database/userdata.json", 'w', encoding="utf-8") as file:
                json.dump(userdata, file, indent="\t", ensure_ascii=False)

            embed = discord.Embed(
                title="레벨 설정 완료",
                description=f"**{user}**의 레벨을 {level}(으)로 설정하였습니다.",
                color=discord.Color.green()
            )
            await context.send(embed=embed)
            Log_channel = discord.utils.get(context.guild.channels,
                                            id=self.bot.config["log_channel_id"])
            await Log_channel.send(embed=log.level_set(context.author.id, level, user.id))

    @ commands.hybrid_group(
        name="xp",
        description="경험치 관련 기능을 제공합니다. (창조자 전용)"
    )
    async def xp(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                title="Error!",
                description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`set` - 유저의 경험치를 설정합니다",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @ xp.command(
        name="set",
        description="유저의 경험치를 설정합니다. (창조자 전용)",
    )
    @ app_commands.describe(user="대상 유저", xp="설정할 경험치")
    @ checks.is_owner()
    async def xp_set(self, context: Context, user: discord.User, xp: int):
        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)

        if str(user.id) not in userdata:
            embed = discord.Embed(
                title="Error!",
                description="유저를 찾을 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

        else:
            userdata[str(user.id)]["xp"] = xp
            with open("database/userdata.json", 'w', encoding="utf-8") as file:
                json.dump(userdata, file, indent="\t", ensure_ascii=False)

            embed = discord.Embed(
                title="레벨 설정 완료",
                description=f"**{user}**의 경험치를 {xp}(으)로 설정하였습니다.",
                color=discord.Color.green()
            )
            await context.send(embed=embed)
            Log_channel = discord.utils.get(context.guild.channels,
                                            id=self.bot.config["log_channel_id"])
            await Log_channel.send(embed=log.xp_set(context.author.id, xp, user.id))

    @xp.command(
        name="info",
        description="경험치 드랍량을 확인합니다. (창조자 전용)",
    )
    @checks.is_owner()
    async def xp_info(self, context: Context):
        global _MAXXP
        global _MINXP

        embed = discord.Embed(
            title="XP INFO",
            description=f"Minimum: `{_MINXP}`\nMaximum: `{_MAXXP}`",
            color=discord.Color.blurple()
        )
        await context.send(embed=embed)

    @xp.command(
        name="min",
        description="경험치 최소 드랍량을 설정합니다. (창조자 전용)",
    )
    @checks.is_owner()
    async def xp_min(self, context: Context, amount: int):
        if amount >= 0:
            global _MINXP

            _MINXP = amount

            embed = discord.Embed(
                title="XP",
                description=f"경험치 최소 드랍량을 `{_MINXP}`(으)로 설정하였습니다.",
                color=discord.Color.green()
            )
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description=f"드랍량은 음수가 될 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @xp.command(
        name="max",
        description="경험치 최소 드랍량을 설정합니다. (창조자 전용)",
    )
    @checks.is_owner()
    async def xp_max(self, context: Context, amount: int):
        if amount >= 0:
            global _MAXXP

            _MAXXP = amount

            embed = discord.Embed(
                title="XP",
                description=f"경험치 최대 드랍량을 `{_MAXXP}`(으)로 설정하였습니다.",
                color=discord.Color.green()
            )
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description=f"드랍량은 음수가 될 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Level(bot))
