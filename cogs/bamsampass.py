import discord
import json
import random
import time
import typing
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from helpers import checks, log, embeds, formatter


PERIDOT_EMOJI = "<:peridot:722474684045721973>"
TOKEN_EMOJI = "<:token:884035217252311051>"


class BSpass(commands.Cog, name="bamsampass"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot: #Bot return
            return
        try:
            if after.channel.id == 1070685834933719071: #잠수방 return
                return
        except:
            pass

        #Generating new userdata
        isPremium = False
        VIProle = member.guild.get_role(853154704664952843)
        if VIProle in member.roles:
            isPremium = True
        with open('database/bpass_userdata.json', encoding="utf-8") as file:
            bpUserdata = json.load(file)
        userid = member.id
        if str(userid) not in bpUserdata:
            newUser = {
                str(userid): {
                    "name": member.display_name,
                    "userid": userid,
                    "premium": isPremium,
                    "level": 0,
                    "xp": 0,
                    "unreceivedPeridot": 0,
                    "unreceivedToken": 0,
                    "unreceivedRole": [],
                    "unreceivedItem": [],
                    "unreceivedPremiumPeridot": 0,
                    "unreceivedPremiumToken": 0,
                    "unreceivedPremiumRole": [],
                    "unreceivedPremiumItem": [],
                    "totalTime": 0,
                    "joinTime": round(time.time())
                }
            }
            bpUserdata.update(newUser)
            with open("database/bpass_userdata.json", 'w', encoding="utf-8") as file:
                json.dump(bpUserdata, file, indent="\t", ensure_ascii=False)


        #Adding XP
        with open('database/bpass_userdata.json', encoding="utf-8") as file:
            bpUserdata = json.load(file)
        
        if bpUserdata[str(userid)]["level"] >= 30:
            return
        if before.channel == None: #Check if new join
            joinTime = round(time.time())
            bpUserdata[str(userid)]["joinTime"] = joinTime
        elif after.channel == None: #Check if leave vc
            leaveTime = round(time.time())
            passedTime = leaveTime - bpUserdata[str(userid)]["joinTime"]
            bpUserdata[str(userid)]["totalTime"] += passedTime
            if bpUserdata[str(userid)]["premium"] == True:
                xp = passedTime * 1.25
            else:
                xp = passedTime
            
            bpUserdata[str(userid)]["xp"] += xp
            bpUserdata[str(userid)]["joinTime"] = None

        with open("database/bpass_userdata.json", 'w', encoding="utf-8") as file:
            json.dump(bpUserdata, file, indent="\t", ensure_ascii=False)


        #Setting Variable
        with open('database/bpass_userdata.json', encoding="utf-8") as file:
            bpUserdata = json.load(file)
        with open("database/bpass_rewards.json", encoding="utf-8") as file:
            bpRewards = json.load(file)
        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)
        with open("database/itemdata.json", encoding="utf-8") as file:
            itemdata = json.load(file)
        currentLevel = bpUserdata[str(userid)]["level"]
        currentXp = bpUserdata[str(userid)]["xp"]
        targetXp = bpRewards[str(currentLevel+1)]["targetxp"]
        normalRewardType = bpRewards[str(currentLevel+1)]["reward"]["type"] #PERIDOT, TOKEN, ROLE, ITEM
        premiumRewardType = bpRewards[str(currentLevel+1)]["premiumReward"]["type"] #PERIDOT, TOKEN, ROLE, ITEM
        isPremium = bpUserdata[str(userid)]["premium"]
        
        #Checking Levelup
        if currentXp >= targetXp: 
            bpUserdata[str(userid)]["xp"] -= bpRewards[str(currentLevel)]["targetxp"]
            bpUserdata[str(userid)]["level"] += 1


            rewardStr = ""
            premiumRewardStr = ""
            #Normal rewarding
            if normalRewardType == "PERIDOT":
                bpUserdata[str(userid)]["unreceivedPeridot"] += bpRewards[str(currentLevel+1)]["reward"]["reward"]
                rewardStr = f"{bpRewards[str(currentLevel+1)]["reward"]["reward"]} {PERIDOT_EMOJI}"
            elif normalRewardType == "TOKEN":
                bpUserdata[str(userid)]["unreceivedToken"] += bpRewards[str(currentLevel+1)]["reward"]["reward"]
                rewardStr = f"{bpRewards[str(currentLevel+1)]["reward"]["reward"]} {TOKEN_EMOJI}"
            elif normalRewardType == "ROLE":
                bpUserdata[str(userid)]["unreceivedRole"].append(bpRewards[str(currentLevel+1)]["reward"]["reward"])
                role = member.guild.get_role(bpRewards[str(currentLevel+1)]["reward"]["reward"])
                rewardStr = f"{role.mention()}"
            elif normalRewardType == "ITEM":
                bpUserdata[str(userid)]["unreceivedItem"].append(bpRewards[str(currentLevel+1)]["reward"]["reward"])
                rewardStr = f"{bpRewards[str(currentLevel+1)]["reward"]["reward"]}"

            #Premium rewarding
            if premiumRewardType == "PERIDOT":
                bpUserdata[str(userid)]["unreceivedPremiumPeridot"] += bpRewards[str(currentLevel+1)]["premiumReward"]["reward"]
                premiumRewardStr = f"{bpRewards[str(currentLevel+1)]["premiumReward"]["reward"]} {PERIDOT_EMOJI}"
            elif premiumRewardType == "TOKEN":
                bpUserdata[str(userid)]["unreceivedPremiumToken"] += bpRewards[str(currentLevel+1)]["premiumReward"]["reward"]
                premiumRewardStr = f"{bpRewards[str(currentLevel+1)]["premiumReward"]["reward"]} {TOKEN_EMOJI}"
            elif premiumRewardType == "ROLE":
                bpUserdata[str(userid)]["unreceivedPremiumRole"].append(bpRewards[str(currentLevel+1)]["premiumReward"]["reward"])
                role = member.guild.get_role(bpRewards[str(currentLevel+1)]["premiumReward"]["reward"])
                premiumRewardStr = f"{role.mention()}"
            elif premiumRewardType == "ITEM":
                bpUserdata[str(userid)]["unreceivedPremiumItem"].append(bpRewards[str(currentLevel+1)]["premiumReward"]["reward"])
                premiumRewardStr = f"{bpRewards[str(currentLevel+1)]["premiumReward"]["reward"]}"

            embed = discord.Embed(
                title="BAMSAMPASS", description=f":tada: **LEVEL UP!** :tada:\nLv.{currentLevel} → Lv.{currentLevel+1}", color=discord.Color.og_blurple())
            embed.add_field(
                name="[일반 보상]", value=f"{rewardStr}", inline=True)
            embed.add_field(
                name="[프리미엄 보상]", value=f"{premiumRewardStr}", inline=True)
            embed.set_footer(text=member.display_name, icon_url=member.display_avatar.url)

            chatChannel = member.guild.get_channel(958025710025453640)
            await chatChannel.send(content=member.mention, embed=embed)


        #Giving reward
        normalPeridot = bpUserdata[str(userid)]["unreceivedPeridot"]
        normalToken = bpUserdata[str(userid)]["unreceivedToken"]
        normalRole = []
        normalItem = []

        userdata[str(userid)]["peridot"] = userdata[str(userid)]["peridot"] + normalPeridot
        bpUserdata[str(userid)]["unreceivedPeridot"] = 0
        userdata[str(userid)]["token"] = userdata[str(userid)]["token"] + normalToken
        bpUserdata[str(userid)]["unreceivedToken"] = 0

        if len(bpUserdata[str(userid)]["unreceivedRole"]) != 0:
            for i in range(len(bpUserdata[str(userid)]["unreceivedRole"])):
                role = member.guild.get_role(bpUserdata[str(userid)]["unreceivedRole"][i])
                normalRole.append(role.mention())
                bpUserdata[str(userid)]["unreceivedRole"].remove(bpUserdata[str(userid)]["unreceivedRole"][i])
        if len(bpUserdata[str(userid)]["unreceivedItem"]) != 0:
            for i in range(len(bpUserdata[str(userid)]["unreceivedItem"])):
                normalItem.append(bpUserdata[str(userid)]["unreceivedItem"][i])
                itemdata[str(userid)]["inventory"].append(bpUserdata[str(userid)]["unreceivedItem"][i])

        if bpUserdata[str(userid)]["premium"] == True:
            premiumPeridot = bpUserdata[str(userid)]["unreceivedPremiumPeridot"]
            premiumToken = bpUserdata[str(userid)]["unreceivedPremiumToken"]
            premiumRole = []
            premiumItem = []

            userdata[str(userid)]["peridot"] = userdata[str(userid)]["peridot"] + premiumPeridot
            bpUserdata[str(userid)]["unreceivedPremiumPeridot"] = 0
            userdata[str(userid)]["token"] = userdata[str(userid)]["token"] + premiumToken
            bpUserdata[str(userid)]["unreceivedPremiumToken"] = 0

            if len(bpUserdata[str(userid)]["unreceivedPremiumRole"]) != 0:
                for i in range(len(bpUserdata[str(userid)]["unreceivedPremiumRole"])):
                    role = member.guild.get_role(bpUserdata[str(userid)]["unreceivedPremiumRole"][i])
                    premiumRole.append(role.mention())
                    bpUserdata[str(userid)]["unreceivedPremiumRole"].remove(bpUserdata[str(userid)]["unreceivedPremiumRole"][i])
            if len(bpUserdata[str(userid)]["unreceivedPremiumItem"]) != 0:
                for i in range(len(bpUserdata[str(userid)]["unreceivedPremiumItem"])):
                    premiumItem.append(bpUserdata[str(userid)]["unreceivedPremiumItem"][i])
                    itemdata[str(userid)]["inventory"].append(bpUserdata[str(userid)]["unreceivedPremiumItem"][i])
                    bpUserdata[str(userid)]["unreceivedPremiumItem"].remove(bpUserdata[str(userid)]["unreceivedPremiumItem"][i])

        with open("database/userdata.json", 'w', encoding="utf-8") as file:
            json.dump(userdata, file, indent="\t", ensure_ascii=False)
        with open("database/itemdata.json", 'w', encoding="utf-8") as file:
            json.dump(userdata, file, indent="\t", ensure_ascii=False)
        with open("database/bpass_userdata.json", 'w', encoding="utf-8") as file:
            json.dump(bpUserdata, file, indent="\t", ensure_ascii=False)


    @commands.hybrid_group(
        name="bamsampass",
        description="뱀샘패스 관련 기능을 제공합니다."
    )
    async def bamsampass(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                title="Error!",
                description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`info` - 뱀샘패스 정보를 확인합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @bamsampass.command(
        name="info",
        description="유저의 뱀샘패스 정보를 확인합니다.",
    )
    @app_commands.describe(user="대상 유저")
    async def bamsampass_info(self, context: Context, user: discord.User = None) -> None:
        if user == None:
            user = context.author

        with open("database/bpass_userdata.json", encoding="utf-8") as file:
            bpUserdata = json.load(file)
        with open("database/bpass_rewards.json", encoding="utf-8") as file:
            bpRewards = json.load(file)

        if str(user.id) not in bpUserdata:
            embed = discord.Embed(
                title=None, description=f"{user.mention}의 뱀샘패스가 생성되지 않았습니다\n먼저 음성 채널에 들어가 뱀샘패스를 생성해주세요.", color=discord.Color.og_blurple())
            embed.set_author(
                name=f"{user.name}'s Bamsampass", icon_url=user.display_avatar.url)
            return await context.send(embed=embed)

        LEVEL = bpUserdata[str(user.id)]["level"]
        XP = bpUserdata[str(user.id)]["xp"]
        TARGETXP = bpRewards[str(LEVEL+1)]["targetxp"]

        ISPREMIUM = "[NORMAL USER]"
        if bpUserdata[str(user.id)]["premium"] == True:
            ISPREMIUM = "[PREMIUM USER]"
        # NORMAL Reward
        REWARD = bpRewards[str(LEVEL+1)]["reward"]["reward"]
        if bpRewards[str(LEVEL+1)]["reward"]["type"] == "PERIDOT":
            EMOJI = PERIDOT_EMOJI
        elif bpRewards[str(LEVEL+1)]["reward"]["type"] == "TOKEN":
            EMOJI = TOKEN_EMOJI
        elif bpRewards[str(LEVEL+1)]["reward"]["type"] == "ROLE":
            EMOJI = ""
            REWARD = f"<@&{REWARD}>"
        elif bpRewards[str(LEVEL+1)]["reward"]["type"] == "ITEM":
            EMOJI = ""
            REWARD = f"{REWARD}"
        else:
            EMOJI = ""

        # Premium Reward
        PREMIUM_REWARD = bpRewards[str(LEVEL+1)]["premiumReward"]["reward"]
        if bpRewards[str(LEVEL+1)]["premiumReward"]["type"] == "PERIDOT":
            PREMIUM_EMOJI = PERIDOT_EMOJI
        elif bpRewards[str(LEVEL+1)]["premiumReward"]["type"] == "TOKEN":
            PREMIUM_EMOJI = TOKEN_EMOJI
        elif bpRewards[str(LEVEL+1)]["premiumReward"]["type"] == "ROLE":
            PREMIUM_EMOJI = ""
            PREMIUM_REWARD = f"<@&{REWARD}>"
        elif bpRewards[str(LEVEL+1)]["premiumReward"]["type"] == "ITEM":
            EMOJI = ""
            REWARD = f"{REWARD}"
        else:
            PREMIUM_EMOJI = ""

        
        storedPeridot = f"{bpUserdata[str(user.id)]["unreceivedPremiumPeridot"]} {PERIDOT_EMOJI}\n"
        storedToken = f"{bpUserdata[str(user.id)]["unreceivedPremiumToken"]} {TOKEN_EMOJI}\n"
        storedRole = f""
        storedItem = f""
        if len(bpUserdata[str(user.id)]["unreceivedPremiumRole"]) != 0:
            for i in range(len(bpUserdata[str(user.id)]["unreceivedPremiumRole"])):
                role = context.guild.get_role(bpUserdata[str(user.id)]["unreceivedPremiumRole"][i])
                storedRole += f"{role.mention}\n"
        
        if len(bpUserdata[str(user.id)]["unreceivedPremiumItem"]) != 0:
            for i in range(len(bpUserdata[str(user.id)]["unreceivedPremiumItem"])):
                storedItem += f"{bpUserdata[str(user.id)]["unreceivedPremiumItem"][i]}\n"


        embed = discord.Embed(
            title=None, description=f"**{ISPREMIUM}**\nLv. {LEVEL}\n「 {format(XP, ',')} / {format(int(TARGETXP), ',')} BXP 」", color=discord.Color.og_blurple())
        embed.set_author(
            name=f"{formatter.remove_wings(user.display_name)}'s Bamsampass", icon_url=user.avatar)
        embed.add_field(
            name="Next Reward", value=f"{REWARD} {EMOJI}", inline=True)
        embed.add_field(name="Next Reward (Premium)",
                        value=f"{PREMIUM_REWARD} {PREMIUM_EMOJI}", inline=True)
        if bpUserdata[str(user.id)]["premium"] == False:
            embed.add_field(name="Stored Premium Rewards",
                            value=f"{storedPeridot+storedToken+storedRole+storedItem}", inline=False)
            embed.set_footer(text="Stored된 보상은 프리미엄 업그레이드시 자동 지급됩니다.")
        await context.send(embed=embed)

    @bamsampass.command(
        name="set",
        description="유저의 뱀샘패스 정보를 수정합니다. (창조자 전용)"
    )
    @checks.is_owner()
    @app_commands.describe(user="대상 유저", type="수정할 정보의 종류", value="수정할 값")
    async def bamsampass_set(self, context: Context, user: discord.User, type: typing.Literal['경험치', '레벨'], value):
        with open("database/bpass_userdata.json", encoding="utf-8") as file:
            bpUserdata = json.load(file)

        if str(user.id) not in bpUserdata:
            embed = discord.Embed(
                title="ERROR", description=f"{user.mention}(을)를 찾을 수 없습니다.", color=discord.Color.red())
            return await context.send(embed=embed)
        
        if type == "경험치":
            bpUserdata[str(user.id)]["xp"] = value
        elif type == "레벨":
            bpUserdata[str(user.id)]["level"] = value
        
        embed = discord.Embed(
                title="Bamsampass", description=f"{user.mention}의 뱀샘패스 {type}(을)를 `{value}`(으)로 수정하였습니다.", color=discord.Color.blurple())
        await context.send(embed=embed)

        with open("database/bpass_userdata.json", 'w', encoding="utf-8") as file:
            json.dump(bpUserdata, file, indent="\t", ensure_ascii=False)


    @bamsampass.command(
        name="setpremium",
        description="유저의 뱀샘패스 프리미엄 여부를 수정합니다. (창조자 전용)"
    )
    @checks.is_owner()
    @app_commands.describe(user="대상 유저", type="수정할 뱀샘패스 종류")
    async def bamsampass_setpremium(self, context: Context, user: discord.User, type: typing.Literal['일반', '프리미엄']):
        with open("database/bpass_userdata.json", encoding="utf-8") as file:
            bpUserdata = json.load(file)

        if str(user.id) not in bpUserdata:
            embed = discord.Embed(
                title="ERROR", description=f"{user.mention}(을)를 찾을 수 없습니다.", color=discord.Color.red())
            return await context.send(embed=embed)
        
        if type == '일반':
            bpUserdata[str(user.id)]["premium"] = False
        elif type == '프리미엄':
            bpUserdata[str(user.id)]["premium"] = True

        embed = discord.Embed(
                title="Bamsampass", description=f"{user.mention}의 뱀샘패스 타입을 {type}으로 수정하였습니다.", color=discord.Color.blurple())
        await context.send(embed=embed)

        with open("database/bpass_userdata.json", 'w', encoding="utf-8") as file:
            json.dump(bpUserdata, file, indent="\t", ensure_ascii=False)


async def setup(bot):
    await bot.add_cog(BSpass(bot))