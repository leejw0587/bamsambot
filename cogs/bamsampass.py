import discord
import json
import random
import time
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from helpers import checks, log, embeds, formatter

xpRatio = 1

PERIDOT_EMOJI = "<:peridot:722474684045721973>"
TOKEN_EMOJI = "<:token:884035217252311051>"


class Bpass(commands.Cog, name="bpass"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        with open('database/bpass_userdata.json', 'r') as file:
            bpUserdata = json.load(file)
        userid = member.id
        if str(userid) not in bpUserdata:
            newUser = {
                str(userid): {
                    "name": member.name,
                    "userid": userid,
                    "premium": False,
                    "level": 0,
                    "xp": 0,
                    "unreceivedPeridot": 0,
                    "unreceivedToken": 0,
                    "unreceivedRole": [],
                    "totalTime": 0,
                    "joinTime": None
                }
            }
            bpUserdata.update(newUser)
            with open("database/bpass_userdata.json", 'w', encoding="utf-8") as file:
                json.dump(bpUserdata, file, indent="\t", ensure_ascii=False)

        if bpUserdata[str(userid)]["level"] >= 30:
            return
        if (before.channel == None):
            joinTime = round(time.time())
            bpUserdata[str(userid)]["joinTime"] = joinTime
        elif after.channel == None:
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

        with open("database/bpass_rewards.json") as file:
            bpRewards = json.load(file)
        currentLevel = bpUserdata[str(userid)]["level"]
        if bpUserdata[str(userid)]["xp"] >= bpRewards[str(currentLevel)]["targetxp"]:
            bpUserdata[str(userid)]["xp"] -= bpRewards[str(currentLevel)]["targetxp"]
            bpUserdata[str(userid)]["level"] += 1

            with open("database/userdata.json", encoding="utf-8") as file:
                userdata = json.load(file)

            if bpRewards[str(currentLevel+1)]["reward"]["type"] == "PERIDOT":
                    userdata[str(userid)]["peridot"] = userdata[str(userid)]["peridot"] + bpRewards[str(currentLevel+1)]["reward"]["reward"]
                    REWARD = bpRewards[str(currentLevel+1)]["reward"]["reward"]
                    EMOJI = PERIDOT_EMOJI
            elif bpRewards[str(currentLevel+1)]["reward"]["type"] == "TOKEN":
                userdata[str(userid)]["token"] = userdata[str(userid)]["token"] + bpRewards[str(currentLevel+1)]["reward"]["reward"]
                REWARD = bpRewards[str(currentLevel+1)]["reward"]["reward"]
                EMOJI = TOKEN_EMOJI
            elif bpRewards[str(currentLevel+1)]["reward"]["type"] == "ROLE":
                role = member.guild.get_role(bpRewards[str(currentLevel+1)]["reward"]["reward"])
                await member.add_roles(role)
                roleid = bpRewards[str(currentLevel+1)]["reward"]["reward"]
                REWARD = f"<@&{roleid}>"
                EMOJI = None
            elif bpRewards[str(currentLevel+1)]["reward"]["type"] == "ITEM":
                REWARD = bpRewards[str(currentLevel+1)]["reward"]["reward"]
                EMOJI = None
                with open("database/itemdata.json", encoding="utf-8") as file:
                    itemdata = json.load(file)
                itemdata[str(member.id)]["inventory"].append(REWARD)

                if REWARD == "개인 통화방 이름 변경권":
                    itemdata[str(member.id)]["voice_title_modify"] = True
                elif REWARD == "개인 통화방 이모지 변경권":
                    itemdata[str(member.id)]["voice_emoji_modify"] = True
                with open("database/itemdata.json", 'w', encoding="utf-8") as file:
                    json.dump(itemdata, file, indent="\t",
                                ensure_ascii=False)
            # if bpUserdata[str(userid)]["premium"] == True:
            #     if bpRewards[str(currentLevel+1)]["premiumReward"]["type"] == "PERIDOT":
            #         userdata[str(userid)]["peridot"] = userdata[str(userid)]["peridot"] + bpRewards[str(currentLevel+1)]["premiumReward"]["reward"]
            #         REWARD = bpRewards[str(currentLevel+1)]["premiumReward"]["reward"]
            #         EMOJI = PERIDOT_EMOJI
            #     elif bpRewards[str(currentLevel+1)]["premiumReward"]["type"] == "TOKEN":
            #         userdata[str(userid)]["token"] = userdata[str(userid)]["token"] + bpRewards[str(currentLevel+1)]["premiumReward"]["reward"]
            #         REWARD = bpRewards[str(currentLevel+1)]["premiumReward"]["reward"]
            #         EMOJI = TOKEN_EMOJI
            #     elif bpRewards[str(currentLevel+1)]["premiumReward"]["type"] == "ROLE":
            #         role = member.guild.get_role(
            #             bpRewards[str(currentLevel+1)]["premiumReward"]["reward"])
            #         await member.add_roles(role)
            #         REWARD = role.mention()
            #         EMOJI = None
            #     elif bpRewards[str(currentLevel+1)]["premiumReward"]["type"] == "ITEM":
            #         REWARD = bpRewards[str(currentLevel+1)]["premiumReward"]["reward"]
            #         EMOJI = None
            #         with open("database/itemdata.json", encoding="utf-8") as file:
            #             itemdata = json.load(file)
            #         itemdata[str(member.id)]["inventory"].append(REWARD)

            #         if REWARD == "개인 통화방 이름 변경권":
            #             itemdata[str(member.id)]["voice_title_modify"] = True
            #         elif REWARD == "개인 통화방 이모지 변경권":
            #             itemdata[str(member.id)]["voice_emoji_modify"] = True
            #         with open("database/itemdata.json", 'w', encoding="utf-8") as file:
            #             json.dump(itemdata, file, indent="\t",
            #                       ensure_ascii=False)
            # else:
                

            with open("database/userdata.json", 'w', encoding="utf-8") as file:
                json.dump(userdata, file, indent="\t", ensure_ascii=False)
            with open("database/bpass_userdata.json", 'w', encoding="utf-8") as file:
                json.dump(bpUserdata, file, indent="\t", ensure_ascii=False)

            embed = discord.Embed(
                title="BAMSAMPASS", description=f":tada: **LEVEL UP!** :tada:\n{currentLevel} → {currentLevel+1}", color=discord.Color.og_blurple())
            embed.add_field(
                name="보상 목록", value=f"{REWARD} {EMOJI}", inline=False)
            await member.send(embed=embed)

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
        description="뱀샘패스 정보를 확인합니다.",
    )
    async def bamsampass_info(self, context: Context) -> None:
        with open("database/bpass_userdata.json") as file:
            bpUserdata = json.load(file)
        with open("database/bpass_rewards.json") as file:
            bpRewards = json.load(file)

        if str(context.author.id) not in bpUserdata:
            newUser = {
                str(context.author.id): {
                    "name": context.author.name,
                    "userid": context.author.id,
                    "premium": False,
                    "level": 0,
                    "xp": 0,
                    "unreceivedPeridot": 0,
                    "unreceivedToken": 0,
                    "unreceivedRole": [],
                    "totalTime": 0,
                    "joinTime": None
                }
            }
            bpUserdata.update(newUser)
            with open("database/bpass_userdata.json", 'w', encoding="utf-8") as file:
                json.dump(bpUserdata, file, indent="\t", ensure_ascii=False)

        LEVEL = bpUserdata[str(context.author.id)]["level"]
        XP = bpUserdata[str(context.author.id)]["xp"]
        TARGETXP = bpRewards[str(LEVEL)]["targetxp"]

        ISPREMIUM = "[NORMAL USER]"
        if bpUserdata[str(context.author.id)]["premium"] == True:
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

        embed = discord.Embed(
            title=None, description=f"**{ISPREMIUM}**\nLv. {LEVEL}\n「 {format(XP, ',')} / {format(int(TARGETXP), ',')} BXP 」", color=discord.Color.og_blurple())
        embed.set_author(
            name=f"{context.author.name}'s Bamsampass", icon_url=context.author.avatar)
        embed.add_field(
            name="Next Reward", value=f"{REWARD} {EMOJI}", inline=False)
        # embed.add_field(name="Next Reward (Premium)",
        #                 value=f"{PREMIUM_REWARD} {PREMIUM_EMOJI}", inline=False)
        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Bpass(bot))
