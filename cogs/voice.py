import discord
import asyncio
import json
import emoji as emo
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import traceback
import sqlite3
import validators

from helpers import checks


class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        conn = sqlite3.connect('database/voice.db')
        c = conn.cursor()
        guildID = member.guild.id
        c.execute("SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
        voice = c.fetchone()
        if voice is None:
            pass
        else:
            voiceID = voice[0]
            try:
                if after.channel.id == voiceID:
                    c.execute(
                        "SELECT * FROM voiceChannel WHERE userID = ?", (member.id,))
                    cooldown = c.fetchone()
                    if cooldown is None:
                        pass
                    else:
                        embed = discord.Embed(
                            title="Error!",
                            description=f"개인 보이스 채널을 너무 빨리 만들지 말아주세요!",
                            color=discord.Color.red()
                        )
                        await member.send(embed=embed)
                        await asyncio.sleep(15)
                    c.execute(
                        "SELECT voiceCategoryID FROM guild WHERE guildID = ?", (guildID,))
                    voice = c.fetchone()
                    c.execute(
                        "SELECT channelName, channelLimit FROM userSettings WHERE userID = ?", (member.id,))
                    setting = c.fetchone()
                    c.execute(
                        "SELECT channelLimit FROM guildSettings WHERE guildID = ?", (guildID,))
                    guildSetting = c.fetchone()
                    if setting is None:
                        try:
                            membername = member.display_name.strip(
                                "༺ৡۣۜ͜ ৡ ""ৡۣۜ͜ ৡ༻ ")
                        except:
                            membername = member.display_name
                        name = f"😊：{membername}의 채널"
                        if guildSetting is None:
                            limit = 0
                        else:
                            limit = guildSetting[0]
                    else:
                        if guildSetting is None:
                            name = setting[0]
                            limit = setting[1]
                        elif guildSetting is not None and setting[1] == 0:
                            name = setting[0]
                            limit = guildSetting[0]
                        else:
                            name = setting[0]
                            limit = setting[1]
                    categoryID = voice[0]
                    id = member.id
                    category = self.bot.get_channel(categoryID)
                    channel2 = await member.guild.create_voice_channel(name, category=category)
                    channelID = channel2.id
                    await member.move_to(channel2)
                    await channel2.set_permissions(self.bot.user, connect=True, read_messages=True)
                    await channel2.edit(name=name, user_limit=limit)
                    c.execute(
                        "INSERT INTO voiceChannel VALUES (?, ?)", (id, channelID))
                    conn.commit()

                    def check(a, b, c):
                        return len(channel2.members) == 0
                    await self.bot.wait_for('voice_state_update', check=check)
                    await channel2.delete()
                    await asyncio.sleep(3)
                    c.execute('DELETE FROM voiceChannel WHERE userID=?', (id,))
            except:
                pass
        conn.commit()
        conn.close()

    @commands.hybrid_group(name="voice", description="보이스 관련 기능을 제공합니다.")
    async def voice(self, context: Context):
        pass

    @voice.command(
        name="setup",
        description="JTC 음성 채널을 설정합니다. (창조자 전용)"
    )
    @app_commands.describe(channelid="등록할 보이스채널의 ID", categoryid="음성 채널이 생성될 카테고리의 ID")
    @checks.is_owner()
    async def voice_setup(self, context: Context, channelid: str, categoryid: str) -> None:
        conn = sqlite3.connect('database/voice.db')
        c = conn.cursor()
        guildID = context.guild.id
        id = context.author.id

        channel = int(channelid)
        new_cat = int(categoryid)

        try:
            c.execute(
                "SELECT * FROM guild WHERE guildID = ? AND ownerID=?", (guildID, id))
            voice = c.fetchone()
            if voice is None:

                c.execute("INSERT INTO guild VALUES (?, ?, ?, ?)",
                          (guildID, id, channel, new_cat))
            else:
                c.execute("UPDATE guild SET guildID = ?, ownerID = ?, voiceChannelID = ?, voiceCategoryID = ? WHERE guildID = ?", (
                    guildID, id, channel, new_cat, guildID))
            await context.send("**JTC 음성 채널 설정이 완료되었습니다.**")
        except Exception as e:
            await context.send(f"설정 도중 오류가 발생했습니다.\n{e}")
        conn.commit()
        conn.close()

    # @commands.hybrid_command()
    # async def setlimit(self, context, num):
    #     conn = sqlite3.connect('database/voice.db')
    #     c = conn.cursor()
    #     if context.author.id == context.guild.owner.id or context.author.id == 424546094182039552:
    #         c.execute("SELECT * FROM guildSettings WHERE guildID = ?",
    #                   (context.guild.id,))
    #         voice = c.fetchone()
    #         if voice is None:
    #             c.execute("INSERT INTO guildSettings VALUES (?, ?, ?)",
    #                       (context.guild.id, f"{context.author.name}'s channel", num))
    #         else:
    #             c.execute(
    #                 "UPDATE guildSettings SET channelLimit = ? WHERE guildID = ?", (num, context.guild.id))
    #         await context.send("You have changed the default channel limit for your server!")
    #     else:
    #         await context.channel.send(f"{context.author.mention} only the owner of the server can setup the bot!")
    #     conn.commit()
    #     conn.close()

    # @setup.error
    # async def info_error(self, context, error):
    #     print(error)

    @voice.command(name="lock", description="본인의 채널을 잠금 설정합니다.")
    async def voice_lock(self, context: Context) -> None:
        conn = sqlite3.connect('database/voice.db')
        c = conn.cursor()
        id = context.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            embed = discord.Embed(
                title="Error!",
                description=f"유저가 소유한 채널을 찾을 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        else:
            channelID = voice[0]
            role = context.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=False)
            embed = discord.Embed(
                title="채널 잠금",
                description=f"채널 잠금 설정이 활성화되었습니다.",
                color=discord.Color.blurple()
            )
            await context.send(embed=embed)
        conn.commit()
        conn.close()

    @voice.command(name="unlock", description="본인의 채널을 잠금 해제합니다.")
    async def voice_unlock(self, context):
        conn = sqlite3.connect('database/voice.db')
        c = conn.cursor()
        id = context.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if voice is None:
            embed = discord.Embed(
                title="Error!",
                description=f"유저가 소유한 채널을 찾을 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        else:
            channelID = voice[0]
            role = context.guild.default_role
            channel = self.bot.get_channel(channelID)
            await channel.set_permissions(role, connect=True)
            embed = discord.Embed(
                title="채널 잠금",
                description=f"채널 잠금 설정이 비활성화되었습니다.",
                color=discord.Color.blurple()
            )
            await context.send(embed=embed)
        conn.commit()
        conn.close()

    @voice.command(name="limit", description="본인의 채널의 최대 인원을 설정합니다.")
    async def voice_limit(self, context: Context, limit: int = 0) -> None:
        conn = sqlite3.connect('database/voice.db')
        c = conn.cursor()
        id = context.author.id
        c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
        voice = c.fetchone()
        if limit > 99:
            embed = discord.Embed(
                title="Error!",
                description=f"최대 인원은 99명 이하로만 설정 가능합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        if limit < 0:
            embed = discord.Embed(
                title="Error!",
                description=f"최대 인원은 0명 이상으로만 설정 가능합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        if voice is None:
            embed = discord.Embed(
                title="Error!",
                description=f"유저가 소유한 채널을 찾을 수 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        else:
            channelID = voice[0]
            channel = self.bot.get_channel(channelID)
            await channel.edit(user_limit=limit)

            if limit == 0:
                limit = '제한 없음'
            else:
                limit = str(limit) + "명"
            embed = discord.Embed(
                title="채널 인원 설정",
                description=f"채널의 최대 인원이 `{limit}`으로 설정되었습니다.",
                color=discord.Color.blurple()
            )
            await context.send(embed=embed)
        conn.commit()
        conn.close()

    # @voice.command(aliases=["allow"])
    # async def permit(self, context, member: discord.Member):
    #     conn = sqlite3.connect('database/voice.db')
    #     c = conn.cursor()
    #     id = context.author.id
    #     c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
    #     voice = c.fetchone()
    #     if voice is None:
    #         await context.channel.send(f"{context.author.mention} You don't own a channel.")
    #     else:
    #         channelID = voice[0]
    #         channel = self.bot.get_channel(channelID)
    #         await channel.set_permissions(member, connect=True)
    #         await context.channel.send(f'{context.author.mention} You have permited {member.name} to have access to the channel. ✅')
    #     conn.commit()
    #     conn.close()

    # @voice.command(aliases=["deny"])
    # async def reject(self, context, member: discord.Member):
    #     conn = sqlite3.connect('database/voice.db')
    #     c = conn.cursor()
    #     id = context.author.id
    #     guildID = context.guild.id
    #     c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
    #     voice = c.fetchone()
    #     if voice is None:
    #         await context.channel.send(f"{context.author.mention} You don't own a channel.")
    #     else:
    #         channelID = voice[0]
    #         channel = self.bot.get_channel(channelID)
    #         for members in channel.members:
    #             if members.id == member.id:
    #                 c.execute(
    #                     "SELECT voiceChannelID FROM guild WHERE guildID = ?", (guildID,))
    #                 voice = c.fetchone()
    #                 channel2 = self.bot.get_channel(voice[0])
    #                 await member.move_to(channel2)
    #         await channel.set_permissions(member, connect=False, read_messages=True)
    #         await context.channel.send(f'{context.author.mention} You have rejected {member.name} from accessing the channel. ❌')
    #     conn.commit()
    #     conn.close()

    # @voice.command()
    # async def limit(self, context, limit):
    #     conn = sqlite3.connect('database/voice.db')
    #     c = conn.cursor()
    #     id = context.author.id
    #     c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
    #     voice = c.fetchone()
    #     if voice is None:
    #         await context.channel.send(f"{context.author.mention} You don't own a channel.")
    #     else:
    #         channelID = voice[0]
    #         channel = self.bot.get_channel(channelID)
    #         await channel.edit(user_limit=limit)
    #         await context.channel.send(f'{context.author.mention} You have set the channel limit to be ' + '{}!'.format(limit))
    #         c.execute(
    #             "SELECT channelName FROM userSettings WHERE userID = ?", (id,))
    #         voice = c.fetchone()
    #         if voice is None:
    #             c.execute("INSERT INTO userSettings VALUES (?, ?, ?)",
    #                       (id, f'{context.author.name}', limit))
    #         else:
    #             c.execute(
    #                 "UPDATE userSettings SET channelLimit = ? WHERE userID = ?", (limit, id))
    #     conn.commit()
    #     conn.close()

    # @voice.command()
    # async def name(self, context, *, name):
    #     conn = sqlite3.connect('database/voice.db')
    #     c = conn.cursor()
    #     id = context.author.id
    #     c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
    #     voice = c.fetchone()
    #     if voice is None:
    #         await context.channel.send(f"{context.author.mention} You don't own a channel.")
    #     else:
    #         channelID = voice[0]
    #         channel = self.bot.get_channel(channelID)
    #         await channel.edit(name=name)
    #         await context.channel.send(f'{context.author.mention} You have changed the channel name to ' + '{}!'.format(name))
    #         c.execute(
    #             "SELECT channelName FROM userSettings WHERE userID = ?", (id,))
    #         voice = c.fetchone()
    #         if voice is None:
    #             c.execute(
    #                 "INSERT INTO userSettings VALUES (?, ?, ?)", (id, name, 0))
    #         else:
    #             c.execute(
    #                 "UPDATE userSettings SET channelName = ? WHERE userID = ?", (name, id))
    #     conn.commit()
    #     conn.close()

    # @voice.command()
    # async def claim(self, context):
    #     x = False
    #     conn = sqlite3.connect('database/voice.db')
    #     c = conn.cursor()
    #     channel = context.author.voice.channel
    #     if channel == None:
    #         await context.channel.send(f"{context.author.mention} you're not in a voice channel.")
    #     else:
    #         id = context.author.id
    #         c.execute(
    #             "SELECT userID FROM voiceChannel WHERE voiceID = ?", (channel.id,))
    #         voice = c.fetchone()
    #         if voice is None:
    #             await context.channel.send(f"{context.author.mention} You can't own that channel!")
    #         else:
    #             for data in channel.members:
    #                 if data.id == voice[0]:
    #                     owner = context.guild.get_member(voice[0])
    #                     await context.channel.send(f"{context.author.mention} This channel is already owned by {owner.mention}!")
    #                     x = True
    #             if x == False:
    #                 await context.channel.send(f"{context.author.mention} You are now the owner of the channel!")
    #                 c.execute(
    #                     "UPDATE voiceChannel SET userID = ? WHERE voiceID = ?", (id, channel.id))
    #         conn.commit()
    #         conn.close()

    @voice.command(name="name", description="본인 채널의 이름을 변경합니다.")
    @app_commands.describe(name="변경할 이름")
    async def voice_name(self, context, name: str):
        with open("database/itemdata.json", encoding="utf-8") as file:
            itemdata = json.load(file)

        if itemdata[str(context.author.id)]["voice_title_modify"] == False:
            embed = discord.Embed(
                title="Error!",
                description=f"`개인 통화방 제목 변경권` 아이템이 필요합니다!",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        else:
            conn = sqlite3.connect('database/voice.db')
            c = conn.cursor()
            id = context.author.id
            c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
            voice = c.fetchone()
            if voice is None:
                embed = discord.Embed(
                    title="Error!",
                    description=f"유저가 소유한 채널을 찾을 수 없습니다.",
                    color=discord.Color.red()
                )
                await context.send(embed=embed)
                return
            else:
                channelID = voice[0]
                channel = self.bot.get_channel(channelID)
                channelName = channel.name
                channelEmoji = channelName[:2]
                await channel.edit(name=f"{channelEmoji}{name}")
                embed = discord.Embed(
                    title="개인 통화방 제목 변경",
                    description=f"개인 통화방의 제목이 `{name}`(으)로 변경되었습니다.",
                    color=discord.Color.blurple()
                )
                await context.send(embed=embed)
            conn.commit()
            conn.close()

    @voice.command(name="emoji", description="본인 채널의 이모지를 변경합니다.")
    @app_commands.describe(emoji="변경할 이모지")
    async def voice_emoji(self, context, emoji: str):
        with open("database/itemdata.json", encoding="utf-8") as file:
            itemdata = json.load(file)

        if itemdata[str(context.author.id)]["voice_emoji_modify"] == False:
            embed = discord.Embed(
                title="Error!",
                description=f"`개인 통화방 이모지 변경권` 아이템이 필요합니다!",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        else:
            conn = sqlite3.connect('database/voice.db')
            c = conn.cursor()
            id = context.author.id
            c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (id,))
            voice = c.fetchone()
            if voice is None:
                embed = discord.Embed(
                    title="Error!",
                    description=f"유저가 소유한 채널을 찾을 수 없습니다.",
                    color=discord.Color.red()
                )
                await context.send(embed=embed)
                return
            if not emo.is_emoji(emoji):
                embed = discord.Embed(
                    title="Error!",
                    description=f"올바른 형식의 이모지가 아닙니다!",
                    color=discord.Color.red()
                )
                await context.send(embed=embed)
                return
            else:
                channelID = voice[0]
                channel = self.bot.get_channel(channelID)
                channelName = channel.name[2:]
                await channel.edit(name=f"{emoji}：{channelName}")
                embed = discord.Embed(
                    title="개인 통화방 이모지 변경",
                    description=f"개인 통화방의 이모지가 `{emoji}`로 변경되었습니다.",
                    color=discord.Color.blurple()
                )
                await context.send(embed=embed)
            conn.commit()
            conn.close()

    @voice.command(name="fix", description="DB Cleaner (개발자 전용)")
    @checks.is_dev()
    async def voice_fix(self, context, userid: str):
        conn = sqlite3.connect('database/voice.db')
        c = conn.cursor()
        id = int(userid)
        c.execute('DELETE FROM voiceChannel WHERE userID=?', (id,))
        conn.commit()
        conn.close()
        await context.send("CLEANED")


async def setup(bot):
    await bot.add_cog(voice(bot))
