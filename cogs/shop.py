import discord
import json
import typing
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, log

PERIDOT_EMOJI = "<:peridot:722474684045721973>"
TOKEN_EMOJI = "<:token:884035217252311051>"


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
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @shop.command(
        name="list",
        description="상점에 등록된 아이템을 확인합니다.",
    )
    async def shop_list(self, context: Context) -> None:
        with open('database/shop.json') as file:
            shopdata = json.load(file)
        embed = discord.Embed(title="BAMSAM SHOP",
                              description="`/shop buy <이름>`: 해당 아이템 구매\n\n· - ┈┈━━ ˚ . ✿ . ˚ ━━┈┈ - · ·", color=discord.Color.purple())
        embed.set_thumbnail(url=context.guild.icon)
        for i in shopdata:
            ITEMNAME = shopdata[i]["NAME"]
            PRICE = shopdata[i]["PRICE"]
            AMOUNT = shopdata[i]["AMOUNT"]
            ID = shopdata[i]["ID"]

            PRICE = format(PRICE, ',d')

            if int(AMOUNT) == -1:
                AMOUNT = "∞"
            if shopdata[i]["CONDITION"] == "CHECK":
                CONDITION = "인증 칭호 보유"
            else:
                CONDITION = "구매 조건 없음"

            embed.add_field(name=f"{PERIDOT_EMOJI} {PRICE} ▫️ {ITEMNAME}",
                            value=f"<@&{ID}> | {AMOUNT} | {CONDITION}", inline=False)

        await context.send(embed=embed)

    @shop.command(
        name="buy",
        description="상점에서 아이템을 구매합니다.",
    )
    @app_commands.describe(item="구매할 아이템")
    async def shop_buy(self, context: Context, item: str) -> None:
        with open('database/shop.json') as file:
            shopdata = json.load(file)
        with open('database/userdata.json') as file:
            userdata = json.load(file)

        CHECKROLE = context.guild.get_role(390821573315002369)
        buyer_peridot = int(userdata[str(context.author.id)]["peridot"])

        if item not in shopdata:
            embed = discord.Embed(
                title="Shop",
                description=f"존재하지 않는 아이템입니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        if shopdata[item]["AMOUNT"] == 0:
            embed = discord.Embed(
                title="Shop",
                description=f"재고가 부족합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        if buyer_peridot < int(shopdata[item]["PRICE"]):
            embed = discord.Embed(
                title="Shop",
                description=f"페리도트가 부족합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        if shopdata[item]["CONDITION"] == "CHECK":
            if CHECKROLE not in context.author.roles:
                embed = discord.Embed(
                    title="Shop",
                    description=f"인증 칭호를 가진 사람만 구매할 수 있는 아이템입니다.",
                    color=discord.Color.red()
                )
                await context.send(embed=embed)
                return

        ##########################
        ##### BUYING SECTION #####
        ##########################
        if shopdata[item]["AMOUNT"] == -1:
            pass
        else:
            shopdata[item]["AMOUNT"] -= 1

        userdata[str(context.author.id)
                 ]["peridot"] -= int(shopdata[item]["PRICE"])
        role = context.guild.get_role(int(shopdata[item]["ID"]))

        with open("database/shop.json", 'w') as file:
            json.dump(shopdata, file, indent="\t",
                      ensure_ascii=False)
        with open("database/userdata.json", 'w') as file:
            json.dump(userdata, file, indent="\t",
                      ensure_ascii=False)
        await context.author.add_roles(role)
        embed = discord.Embed(
            title="Shop",
            description=f"`{item}`을(를) 구매하였습니다.",
            color=discord.Color.green()
        )
        await context.send(embed=embed)
        Log_channel = discord.utils.get(context.guild.channels,
                                        id=self.bot.config["log_channel_id"])
        await Log_channel.send(log.shop_buy(context, item))

    @shop.command(
        name="add",
        description="상점에 아이템을 추가합니다. (창조자 전용)",
    )
    @app_commands.describe(item="아이템 이름", roleid="역할ID", price="가격", amount="개수", condition="구매 조건")
    @checks.is_owner()
    async def shop_add(self, context: Context, item: str, roleid: str, price: int, amount: int, condition: typing.Literal['인증 칭호 보유'] = None) -> None:
        with open('database/shop.json') as file:
            shopdata = json.load(file)

        if condition == "인증 칭호 보유":
            condition = "CHECK"

        newItem = {
            item: {
                "NAME": item,
                "TYPE": "ROLE",
                        "ID": int(roleid),
                        "PRICE": price,
                        "AMOUNT": amount,
                        "CONDITION": condition
            }
        }
        shopdata.update(newItem)
        with open("database/shop.json", 'w') as file:
            json.dump(shopdata, file, indent="\t",
                      ensure_ascii=False)
        embed = discord.Embed(
            title="Shop",
            description=f"`{item}`을(를) 상점에 등록하였습니다.",
            color=discord.Color.green()
        )
        await context.send(embed=embed)

    @shop.command(
        name="remove",
        description="상점에서 아이템을 제거합니다. (창조자 전용)",
    )
    @app_commands.describe(item="아이템 이름")
    @checks.is_owner()
    async def shop_remove(self, context: Context, item: str):
        with open('database/shop.json') as file:
            shopdata = json.load(file)

        if item not in shopdata:
            embed = discord.Embed(
                title="Shop",
                description=f"존재하지 않는 아이템입니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        else:
            del (shopdata[item])
            with open("database/shop.json", 'w') as file:
                json.dump(shopdata, file, indent="\t",
                          ensure_ascii=False)
            embed = discord.Embed(
                title="Shop",
                description=f"`{item}`을(를) 삭제했습니다.",
                color=discord.Color.orange()
            )
            await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Shop(bot))
