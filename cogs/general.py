import platform
import random
import json
import time
import datetime
import asyncio
import typing

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Context

from helpers import checks, embeds

PERIDOT_EMOJI = "<:peridot:722474684045721973>"
TOKEN_EMOJI = "<:token:884035217252311051>"


class CreatePcButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label="승인", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "승인"
        self.stop()

    @discord.ui.button(label="거부", style=discord.ButtonStyle.red)
    async def refuse(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "거부"
        self.stop()


class RockPaperScissors(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="가위", description="가위를 냅니다", emoji="✂️"
            ),
            discord.SelectOption(
                label="바위", description="바위를 냅니다", emoji="🪨"
            ),
            discord.SelectOption(
                label="보", description="보를 냅니다.", emoji="🧻"
            ),
        ]
        super().__init__(
            placeholder="무엇을 낼지 선택해주세요",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        choices = {
            "바위": 0,
            "보": 1,
            "가위": 2,
        }
        user_choice = self.values[0].lower()

        user_choice_index = choices[user_choice]
        user_win = False

        user_choice_emoji = ""
        if user_choice_index == 0:
            user_choice_emoji = "🪨"
        elif user_choice_index == 1:
            user_choice_emoji = "🧻"
        elif user_choice_index == 2:
            user_choice_emoji = "✂️"
        user_choice = user_choice + " " + user_choice_emoji

        bot_choice = random.choice(list(choices.keys()))
        bot_choice_index = choices[bot_choice]

        bot_choice_emoji = ""
        if bot_choice_index == 0:
            bot_choice_emoji = "🪨"
        elif bot_choice_index == 1:
            bot_choice_emoji = "🧻"
        elif bot_choice_index == 2:
            bot_choice_emoji = "✂️"
        bot_choice = bot_choice + " " + bot_choice_emoji

        result_embed = discord.Embed(color=0x9C84EF)
        result_embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url
        )

        if user_choice_index == bot_choice_index:
            result_embed.description = f"**비겼습니다!**\n유저의 선택: {user_choice}\n뱀샘봇의 선택: {bot_choice}"
            result_embed.colour = 0xF59E42
        elif user_choice_index == 0 and bot_choice_index == 2:
            result_embed.description = f"**당신이 이겼습니다!**\n유저의 선택: {user_choice}\n뱀샘봇의 선택: {bot_choice}"
            result_embed.colour = 0x9C84EF
            user_win = True
        elif user_choice_index == 1 and bot_choice_index == 0:
            result_embed.description = f"**당신이 이겼습니다!**\n유저의 선택: {user_choice}\n뱀샘봇의 선택: {bot_choice}"
            result_embed.colour = 0x9C84EF
            user_win = True
        elif user_choice_index == 2 and bot_choice_index == 1:
            result_embed.description = f"**당신이 이겼습니다!**\n유저의 선택: {user_choice}\n뱀샘봇의 선택: {bot_choice}"
            result_embed.colour = 0x9C84EF
            user_win = True
        else:
            result_embed.description = f"**뱀샘봇이 이겼습니다!**\n유저의 선택: {user_choice}\n뱀샘봇의 선택: {bot_choice}"
            result_embed.colour = 0xE02B2B

        if user_win == True:
            pass

        await interaction.response.edit_message(embed=result_embed, content=None, view=None)


class RockPaperScissorsView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(RockPaperScissors())


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        description="실행 가능한 모든 커맨드를 표시합니다."
    )
    @checks.not_blacklisted()
    async def help(self, context: Context) -> None:
        prefix = self.bot.config["prefix"]
        embed = discord.Embed(
            title="Help", description="뱀샘봇의 커맨드들: ", color=0x9C84EF)
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            data = []
            for command in commands:
                description = command.description.partition('\n')[0]
                data.append(f"{prefix}{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(name=i.capitalize(),
                            value=f'```{help_text}```', inline=False)
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="botinfo",
        description="봇에 대한 정보를 나타냅니다",
    )
    @checks.not_blacklisted()
    async def botinfo(self, context: Context) -> None:

        config = self.bot.config

        embed = discord.Embed(
            description="Dev By xDxD#6779",
            color=0x9C84EF
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner:",
            value="xDxD#6779",
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{platform.python_version()}",
            inline=True
        )
        embed.add_field(
            name="Bot Version:",
            value=f"{config['version']}",
            inline=False
        )
        # embed.add_field(
        #     name="Prefix:",
        #     value=f"/ (Slash Commands) or {self.bot.config['prefix']} for normal commands",
        #     inline=False
        # )
        embed.set_footer(
            text=f"Requested by {context.author}"
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        description="서버에 대한 정보를 나타냅니다.",
    )
    @checks.not_blacklisted()
    async def serverinfo(self, context: Context) -> None:
        roles = [role.name for role in context.guild.roles]
        if len(roles) > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title="**Server Name:**",
            description=f"{context.guild}",
            color=0x9C84EF
        )
        if context.guild.icon is not None:
            embed.set_thumbnail(
                url=context.guild.icon.url
            )
        embed.add_field(
            name="Server ID",
            value=context.guild.id
        )
        embed.add_field(
            name="Member Count",
            value=context.guild.member_count
        )
        embed.add_field(
            name="Text/Voice Channels",
            value=f"{len(context.guild.channels)}"
        )
        embed.add_field(
            name=f"Roles ({len(context.guild.roles)})",
            value=roles
        )
        embed.set_footer(
            text=f"Created at: {context.guild.created_at}"
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="봇의 레이턴시를 확인합니다.",
    )
    @checks.not_blacklisted()
    async def ping(self, context: Context) -> None:
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x9C84EF
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="attendance",
        description="출석 체크 커맨드입니다.",
    )
    async def attendance(self, context: Context) -> None:
        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)

        today = str(datetime.date.today())
        try:
            attendance_count = userdata[str(context.author.id)]["attendance"]

            if userdata[str(context.author.id)]["last_attendance"] == today:
                embed = discord.Embed(
                    title="Error!",
                    description=f"오늘({today})이미 출석을 했습니다!\n누적 출석 횟수: `{attendance_count}`회",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
            else:

                reward = random.randint(1, 100)

                userdata[str(context.author.id)]["last_attendance"] = today
                userdata[str(context.author.id)]["attendance"] += 1
                userdata[str(context.author.id)]["peridot"] = userdata[str(
                    context.author.id)]["peridot"] + int(reward)
                with open("database/userdata.json", 'w', encoding="utf-8") as file:
                    json.dump(userdata, file, indent="\t", ensure_ascii=False)

                attendance_count = userdata[str(
                    context.author.id)]["attendance"]

                embed = discord.Embed(
                    title="출석 완료!",
                    description=f"`{today}` 출석을 완료했습니다!\n누적 출석 횟수: `{attendance_count}`회\n출석 보상: {reward} {PERIDOT_EMOJI}",
                    color=0x9C84EF
                )

                await context.send(embed=embed)
        except:
            embed = discord.Embed(
                title="Error!",
                description="유저를 찾을 수 없습니다.\n`/inventory`커맨드를 한 번 실행한 후 다시 시도해주세요.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="rps",
        description="뱀샘봇과 가위바위보를 합니다."
    )
    async def rock_paper_scissors(self, context: Context) -> None:
        view = RockPaperScissorsView()
        await context.send("가위, 바위, 보!", view=view)

    @commands.hybrid_command(
        name="createpc",
        description="개인 채널 생성 요청을 보냅니다."
    )
    # @commands.has_role(706453703745601546)
    @app_commands.describe(nickname="채널 주인의 한글 닉네임", channelname="채널 이름", genere="채널의 장르", description="채널 설명", restrictions="채널을 볼 수 있는 역할")
    async def createpc(self, context: Context, nickname: str, channelname: str, genere: str, description: str, restrictions: typing.Literal['모두', '인증', '변태', '그로테스크']):

        if context.channel.id == 706526566104170607:
            # if context.channel.id == 958025710025453640: for dev server
            admin_channel = context.guild.get_channel(936533151721861201)
            # admin_channel = context.guild.get_channel(1062130045340110978) for dev server
            category = context.guild.get_channel(706452195272556586)

            Check_RoleID = 390821573315002369
            Pervert_RoleID = 470942757574279168
            Grot_RoleID = 722663541437497354

            buttons = CreatePcButtons()
            embed = discord.Embed(color=0x9C84EF)
            embed.add_field(
                name="개인 채널 생성 요청", value=f"요청인: {context.author}({nickname})\n채널 이름: {channelname}\n장르: {genere}\n설명: {description}\n역할 제한: {restrictions}", inline=False)
            req_message = await admin_channel.send(embed=embed, view=buttons)
            respond = await context.channel.send("개인 채널 생성 요청을 성공적으로 전송하였습니다.\n잠시만 기다려주세요...")
            await context.defer()
            await buttons.wait()
            if buttons.value == "승인":

                NSFW = False
                if restrictions == "모두":
                    restrictions = context.guild.get_role(context.guild.id)
                elif restrictions == "인증":
                    restrictions = context.guild.get_role(Check_RoleID)
                elif restrictions == "변태":
                    restrictions = context.guild.get_role(Pervert_RoleID)
                    NSFW = True
                elif restrictions == "그로테스크":
                    restrictions = context.guild.get_role(Grot_RoleID)
                    NSFW = True

                new_channel = await context.guild.create_text_channel(name=f"{nickname}ㆍ{channelname}", topic=f"장르 : {genere}", category=category, nsfw=NSFW)
                await new_channel.set_permissions(context.guild.get_role(context.guild.id),
                                                  send_messages=False,
                                                  read_messages=False)
                await new_channel.set_permissions(context.author,
                                                  send_messages=True,
                                                  read_messages=True,
                                                  add_reactions=True,
                                                  embed_links=True,
                                                  attach_files=True,
                                                  read_message_history=True,
                                                  external_emojis=True)
                await new_channel.set_permissions(restrictions,
                                                  send_messages=False,
                                                  read_messages=True,
                                                  add_reactions=True,
                                                  embed_links=True,
                                                  attach_files=True,
                                                  read_message_history=True,
                                                  external_emojis=True)
                embed = discord.Embed(color=0x17fd5c)
                embed.add_field(name="개인 채널 생성 요청",
                                value=f"개인 채널 생성 요청이 승인되었습니다.\n생성된 채널: <#{new_channel.id}>", inline=False)
                await respond.edit(content=" ", embed=embed)

            else:
                embed = discord.Embed(color=0xe92b2b)
                embed.add_field(name="개인 채널 생성 요청",
                                value="개인 채널 생성 요청이 거부되었습니다.", inline=False)
                await respond.edit(content=" ", embed=embed)
            await req_message.delete()

        else:
            embed = discord.Embed(color=0xe92b2b)
            embed.add_field(name="개인 채널 생성 요청",
                            value="해당 명령어는 <#706526566104170607> 에서만 작동합니다.", inline=False)
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="세배",
        description="뱀샘봇에게 세배를 하여 세뱃돈을 받습니다."
    )
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @app_commands.describe(hard="열심히 세배를 할지 선택합니다.")
    async def 세배(self, context: Context, hard: bool = False):
        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)

        if hard == False:
            userdata[str(context.author.id)]["token"] = userdata[str(
                context.author.id)]["token"] + 1
            await context.send(embed=embeds.EmbedBlurple("세배", f"세배를 하여 2 {TOKEN_EMOJI}를 얻었습니다!"))
        else:
            userdata[str(context.author.id)]["token"] = userdata[str(
                context.author.id)]["token"] + 3
            await context.send(embed=embeds.EmbedBlurple("세배", f"열심히 세배를 하여 3 {TOKEN_EMOJI}를 얻었습니다!"))

        with open("database/userdata.json", 'w', encoding="utf-8") as file:
            json.dump(userdata, file, indent="\t", ensure_ascii=False)


async def setup(bot):
    await bot.add_cog(General(bot))
