import discord
import json
import random
import typing
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from helpers import checks, log, formatter

PERIDOT_EMOJI = "<:peridot:722474684045721973>"
TOKEN_EMOJI = "<:token:884035217252311051>"


class Inventory(commands.Cog, name="inventory"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="inventory",
        description="유저의 인벤토리를 확인합니다.",
    )
    @app_commands.describe(user="대상 유저")
    async def inventory(self, context: Context, user: discord.User = None) -> None:
        if user == None:
            user = context.author

        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)
        if str(user.id) in userdata:
            pass
        else:
            newUser = {
                str(user.id): {
                    "username": str(user),
                    "userid": str(user.id),
                    "peridot": 0,
                    "token": 0,
                    "xp": 0,
                    "level": 0,
                    "attendance": 0,
                    "last_attendance": ""
                }
            }
            userdata.update(newUser)
            with open("database/userdata.json", 'w', encoding="utf-8") as file:
                json.dump(userdata, file, indent="\t", ensure_ascii=False)

        with open("database/userdata.json") as file:
            userdata = json.load(file)
        USERNAME = userdata[str(user.id)]["username"]
        USERID = userdata[str(user.id)]["userid"]
        PERIDOT = userdata[str(user.id)]["peridot"]
        TOKEN = userdata[str(user.id)]["token"]
        XP = formatter.numtostr(userdata[str(user.id)]["xp"])
        LEVEL = userdata[str(user.id)]["level"]

        TARGETXP = formatter.numtostr((LEVEL + 1) * 100)
        PERIDOT = format(PERIDOT, ',d')

        embed = discord.Embed(
            title=None, description=f"Lv. {LEVEL}\n「 {XP} / {TARGETXP} EXP 」", color=discord.Color.random())
        embed.set_author(name=f"{USERNAME}'s Inventory",
                         icon_url=user.avatar)
        embed.add_field(
            name="Wallet", value=f"{PERIDOT_EMOJI} {PERIDOT}\n{TOKEN_EMOJI} {TOKEN}", inline=False)
        await context.send(embed=embed)

    @commands.hybrid_group(
        name="peridot",
        description="유저의 페리도트를 관리합니다. (창조자 전용)",
    )
    async def peridot(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                title="Error!",
                description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`add` - 유저에게 페리도트를 추가합니다.\n`remove` - 유저로부터 페리도트를 제거합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @peridot.command(
        name="add",
        description="유저에게 페리도트를 추가합니다. (창조자 전용)",
    )
    @app_commands.describe(user="대상 유저", amount="추가할 양")
    @checks.is_owner()
    async def peridot_add(self, context: Context, user: discord.User, *, amount: int) -> None:
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
            userdata[str(user.id)]["peridot"] = userdata[str(
                user.id)]["peridot"] + int(amount)
            with open("database/userdata.json", 'w', encoding="utf-8") as file:
                json.dump(userdata, file, indent="\t", ensure_ascii=False)

            amount = format(amount, ',d')

            embed = discord.Embed(
                title="페리도트 추가 완료",
                description=f"**{user}**에게 **{amount}** {PERIDOT_EMOJI}를 추가하였습니다.",
                color=discord.Color.green()
            )
            await context.send(embed=embed)
            Log_channel = discord.utils.get(context.guild.channels,
                                            id=self.bot.config["log_channel_id"])
            await Log_channel.send(embed=log.peridot_add(context.author.id, amount, user.id))

    @peridot.command(
        name="remove",
        description="유저로부터 페리도트를 제거합니다. (창조자 전용)",
    )
    @app_commands.describe(user="대상 유저", amount="제거할 양")
    @checks.is_owner()
    async def peridot_remove(self, context: Context, user: discord.User, *, amount: int) -> None:
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
            if userdata[str(user.id)]["peridot"] < amount:
                embed = discord.Embed(
                    title="Error!",
                    description="최종 페리도트는 음수가 될 수 없습니다.",
                    color=discord.Color.red()
                )
                await context.send(embed=embed)
            else:
                userdata[str(user.id)]["peridot"] = userdata[str(
                    user.id)]["peridot"] - int(amount)
                with open("database/userdata.json", 'w', encoding="utf-8") as file:
                    json.dump(userdata, file, indent="\t", ensure_ascii=False)

                amount = format(amount, ',d')

                embed = discord.Embed(
                    title="페리도트 제거 완료",
                    description=f"**{user}**로부터 **{amount}** {PERIDOT_EMOJI}를 제거하였습니다.",
                    color=discord.Color.green()
                )
                await context.send(embed=embed)
                Log_channel = discord.utils.get(context.guild.channels,
                                                id=self.bot.config["log_channel_id"])
                await Log_channel.send(embed=log.peridot_remove(context.author.id, amount, user.id))

    @commands.hybrid_group(
        name="token",
        description="유저의 토큰을 관리합니다.",
    )
    async def token(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                title="Error!",
                description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`add` - 유저에게 토큰을 추가합니다.\n`remove` - 유저로부터 토큰을 제거합니다.\n`open` - 토큰을 개봉합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @token.command(
        name="add",
        description="유저에게 토큰을 추가합니다. (창조자 전용)",
    )
    @app_commands.describe(user="대상 유저", amount="추가할 개수")
    @checks.is_owner()
    async def token_add(self, context: Context, user: discord.User, *, amount: int) -> None:
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
            userdata[str(user.id)]["token"] = userdata[str(
                user.id)]["token"] + int(amount)
            with open("database/userdata.json", 'w', encoding="utf-8") as file:
                json.dump(userdata, file, indent="\t", ensure_ascii=False)

            embed = discord.Embed(
                title="토큰 추가 완료",
                description=f"**{user}**에게 **{amount}** {TOKEN_EMOJI}을 추가하였습니다.",
                color=discord.Color.green()
            )
            await context.send(embed=embed)
            Log_channel = discord.utils.get(context.guild.channels,
                                            id=self.bot.config["log_channel_id"])
            await Log_channel.send(embed=log.token_add(context.author.id, amount, user.id))

    @token.command(
        name="remove",
        description="유저로부터 토큰을 제거합니다. (창조자 전용)",
    )
    @app_commands.describe(user="대상 유저", amount="제거할 개수")
    @checks.is_owner()
    async def token_remove(self, context: Context, user: discord.User, *, amount: int) -> None:
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
            if userdata[str(user.id)]["token"] < amount:
                embed = discord.Embed(
                    title="Error!",
                    description="최종 토큰은 음수가 될 수 없습니다.",
                    color=discord.Color.red()
                )
                await context.send(embed=embed)
            else:
                userdata[str(user.id)]["token"] = userdata[str(
                    user.id)]["token"] - int(amount)
                with open("database/userdata.json", 'w', encoding="utf-8") as file:
                    json.dump(userdata, file, indent="\t", ensure_ascii=False)

                embed = discord.Embed(
                    title="토큰 제거 완료",
                    description=f"**{user}**로부터 **{amount}** {TOKEN_EMOJI}을 제거하였습니다.",
                    color=discord.Color.green()
                )
                await context.send(embed=embed)
                Log_channel = discord.utils.get(context.guild.channels,
                                                id=self.bot.config["log_channel_id"])
                await Log_channel.send(embed=log.token_remove(context.author.id, amount, user.id))

    @token.command(
        name="open",
        description="본인의 토큰을 개봉합니다",
    )
    async def token_open(self, context: Context, amount: int = 1) -> None:
        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)

        if userdata[str(context.author.id)]["token"] <= 0:
            embed = discord.Embed(
                title="Error!",
                description="개봉할 토큰이 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        elif userdata[str(context.author.id)]["token"] < amount:
            embed = discord.Embed(
                title="Error!",
                description="보유한 토큰보다 많이 개봉할 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        else:
            peridot_sum = 0
            for i in range(amount):
                userdata[str(context.author.id)]["token"] = userdata[str(
                    context.author.id)]["token"] - 1

                result = random.randint(1, 1000)
                peridot_sum = peridot_sum + result

            userdata[str(context.author.id)]["peridot"] = userdata[str(
                context.author.id)]["peridot"] + peridot_sum
            with open("database/userdata.json", 'w', encoding="utf-8") as file:
                json.dump(userdata, file, indent="\t", ensure_ascii=False)

            peridot_sum = format(peridot_sum, ',d')

            embed = discord.Embed(
                title="토큰 개봉",
                description=f"토큰을 `{amount}`개 개봉하여 총 **{peridot_sum}** {PERIDOT_EMOJI}를 얻었습니다!",
                color=discord.Color.green()
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="give",
        description="보유한 아이템을 다른 유저에게 줍니다."
    )
    @app_commands.describe(user="대상 유저", type="보낼 아이템 종류", amount="보낼 아이템의 양")
    async def give(self, context: Context, user: discord.User, type: typing.Literal['peridot', 'token'], amount: int):
        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)

        # 대상 유저가 없는 경우
        if userdata[str(user.id)] == None:
            embed = discord.Embed(
                title="Error!",
                description="대상 유저를 찾을 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        # 0 이하를 주는 경우
        elif amount <= 0:
            embed = discord.Embed(
                title="Error!",
                description="0 이하는 보낼 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        # 자신한테 주는 경우
        elif context.author.id == user.id:
            embed = discord.Embed(
                title="Error!",
                description="자신한테 보낼 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        # 보유한 아이템보다 더 많이 주는 경우
        elif userdata[str(context.author.id)][type] < amount:
            embed = discord.Embed(
                title="Error!",
                description="보유한 아이템보다 더 많이 보낼 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        else:
            userdata[str(context.author.id)][type] = userdata[str(
                context.author.id)][type] - amount
            userdata[str(user.id)][type] = userdata[str(
                user.id)][type] + amount

            with open("database/userdata.json", 'w', encoding="utf-8") as file:
                json.dump(userdata, file, indent="\t", ensure_ascii=False)

            emoji = None
            if type == "peridot":
                emoji = PERIDOT_EMOJI
            if type == "token":
                emoji = TOKEN_EMOJI

            embed = discord.Embed(
                title="아이템 전송",
                description=f"{user.mention}에게 {format(amount, ',d')} {emoji}를 전송하였습니다.",
                color=discord.Color.green()
            )
            await context.send(embed=embed)

            Log_channel = discord.utils.get(context.guild.channels,
                                            id=self.bot.config["log_channel_id"])
            await Log_channel.send(embed=log.give(context.author.id, user.id, type, amount))


async def setup(bot):
    await bot.add_cog(Inventory(bot))
