import discord
import json
import typing
import asyncio
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
                description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`list` - 상점에 등록된 아이템을 확인합니다.\n`buy` - 등록된 아이템을 구매합니다.\n`addrole` - 상점에 역할을 추가합니다.\n`additem` - 상점에 아이템을 추가합니다.\n`remove` - 상점에서 아이템을 제거합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @shop.command(
        name="update",
        description="상점 메시지를 새로 등록합니다. (창조자 전용)",
    )
    @checks.is_owner()
    async def shop_update(self, context: Context) -> None:
        shopChannel = context.guild.get_channel(1276799909856804874)
        await shopChannel.purge(limit=1)

        with open('database/shop.json') as file:
            shopdata = json.load(file)
        embed = discord.Embed(title="BAMSAM SHOP",
                              description="`/shop buy <이름>`: 해당 아이템 구매\n\n· - ┈┈━━ ˚ . ✿ . ˚ ━━┈┈ - · ·", color=discord.Color.purple())
        embed.set_thumbnail(url=context.guild.icon)

        for i in shopdata:
            if shopdata[i]["TYPE"] == "ROLE":
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
            elif shopdata[i]["TYPE"] == "ITEM":
                ITEMNAME = shopdata[i]["NAME"]
                PRICE = shopdata[i]["PRICE"]
                AMOUNT = shopdata[i]["AMOUNT"]

                PRICE = format(PRICE, ',d')

                if int(AMOUNT) == -1:
                    AMOUNT = "∞"
                if shopdata[i]["CONDITION"] == "CHECK":
                    CONDITION = "인증 칭호 보유"
                else:
                    CONDITION = "구매 조건 없음"

                embed.add_field(name=f"{PERIDOT_EMOJI} {PRICE} ▫️ {ITEMNAME}",
                                value=f"| {AMOUNT} | {CONDITION}", inline=False)

        await shopChannel.send(embed=embed)

    @shop.command(
        name="buy",
        description="상점에서 아이템을 구매합니다.",
    )
    @app_commands.describe(item="구매할 아이템")
    async def shop_buy(self, context: Context, item: str) -> None:
        if context.channel.id != 1276799909856804874:
            embed = discord.Embed(
                title="Shop",
                description=f"구매는 <#1276799909856804874>에서만 가능합니다.",
                color=discord.Color.red()
            )
            return await context.send(embed=embed)
            
        with open('database/shop.json') as file:
            shopdata = json.load(file)
        with open('database/userdata.json') as file:
            userdata = json.load(file)
        with open('database/itemdata.json') as file:
            itemdata = json.load(file)

        CHECKROLE = context.guild.get_role(1070680727009632297)
        buyer_peridot = int(userdata[str(context.author.id)]["peridot"])

        if item not in shopdata:
            embed = discord.Embed(
                title="Shop",
                description=f"존재하지 않는 아이템입니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed, delete_after=15)
            return
        if shopdata[item]["AMOUNT"] == 0:
            embed = discord.Embed(
                title="Shop",
                description=f"재고가 부족합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed, delete_after=15)
            return
        if buyer_peridot < int(shopdata[item]["PRICE"]):
            embed = discord.Embed(
                title="Shop",
                description=f"페리도트가 부족합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed, delete_after=15)
            return
        if shopdata[item]["CONDITION"] == "CHECK":
            if CHECKROLE not in context.author.roles:
                embed = discord.Embed(
                    title="Shop",
                    description=f"인증 칭호를 가진 사람만 구매할 수 있는 아이템입니다.",
                    color=discord.Color.red()
                )
                await context.send(embed=embed, delete_after=15)
                return

        ##########################
        ##### BUYING SECTION #####
        ##########################
        userdata[str(context.author.id)
                 ]["peridot"] -= int(shopdata[item]["PRICE"])

        if shopdata[item]["TYPE"] == "ROLE":
            if shopdata[item]["NAME"] == "인증":
                Guest_Role = context.guild.get_role(1070680657166090330)
                if Guest_Role in context.author.roles:  # Checking if user has Guest role
                    await context.author.remove_roles(Guest_Role)
            role = context.guild.get_role(int(shopdata[item]["ID"]))
            await context.author.add_roles(role)
        elif shopdata[item]["TYPE"] == "ITEM":
            if shopdata[item]["NAME"] == "개인 통화방 이모지 변경권":
                itemdata[str(context.author.id)]["voice_emoji_modify"] = True
            elif shopdata[item]["NAME"] == "개인 통화방 이름 변경권":
                itemdata[str(context.author.id)]["voice_title_modify"] = True
            itemdata[str(context.author.id)]["inventory"].append(item)

        if shopdata[item]["AMOUNT"] == -1:
            pass
        else:
            shopdata[item]["AMOUNT"] -= 1

        with open("database/shop.json", 'w') as file:
            json.dump(shopdata, file, indent="\t",
                      ensure_ascii=False)
        with open("database/userdata.json", 'w') as file:
            json.dump(userdata, file, indent="\t",
                      ensure_ascii=False)
        with open("database/itemdata.json", 'w') as file:
            json.dump(itemdata, file, indent="\t",
                      ensure_ascii=False)

        embed = discord.Embed(
            title="Shop",
            description=f"`{item}`을(를) 구매하였습니다.",
            color=discord.Color.green()
        )
        msg = await context.send(embed=embed)
        Log_channel = discord.utils.get(context.guild.channels,
                                        id=self.bot.config["log_channel_id"])
        await Log_channel.send(embed=log.shop_buy(context.author.id, item))

        await asyncio.sleep(15)
        await msg.delete()
        self.shop_update(context)




    @shop.command(
        name="addrole",
        description="상점에 역할을 추가합니다. (창조자 전용)",
    )
    @app_commands.describe(item="아이템 이름", roleid="역할ID", price="가격", amount="개수", condition="구매 조건")
    @checks.is_owner()
    async def shop_addrole(self, context: Context, item: str, roleid: str, price: int, amount: int, condition: typing.Literal['없음', '인증 칭호 보유']) -> None:
        with open('database/shop.json') as file:
            shopdata = json.load(file)

        if condition == "없음":
            condition = None
        elif condition == "인증 칭호 보유":
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
        name="additem",
        description="상점에 아이템을 추가합니다. (창조자 전용)",
    )
    @app_commands.describe(item="아이템 이름", price="가격", amount="개수", condition="구매 조건")
    @checks.is_owner()
    async def shop_additem(self, context: Context, item: str, price: int, amount: int, condition: typing.Literal['없음', '인증 칭호 보유']) -> None:
        with open('database/shop.json') as file:
            shopdata = json.load(file)

        if condition == "없음":
            condition = None
        elif condition == "인증 칭호 보유":
            condition = "CHECK"

        newItem = {
            item: {
                "NAME": item,
                "TYPE": "ITEM",
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
