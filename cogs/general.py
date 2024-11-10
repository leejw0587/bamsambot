import platform
import random
import json
import string
import time
import asyncio
import typing
import yt_dlp
import re
import glob
import aiohttp
import discord
import os
import secrets
from yt_dlp import YoutubeDL
from datetime import datetime, date
from discord import app_commands, ui
from discord.ext import commands, tasks
from discord.ext.commands import Context

from helpers import checks, embeds, log

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

class ReportModal(ui.Modal, title='개발자에게 연락'):
    type = ui.TextInput(label="종류", style=discord.TextStyle.short,
                        placeholder="버그 / 신고 / 건의", required=True, max_length=10)
    content = ui.TextInput(label="내용", style=discord.TextStyle.long,
                           placeholder="여기에 내용을 입력해주세요", required=True)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        dev = interaction.guild.get_member(424546094182039552)
        embed = discord.Embed(
            title="New Contact",
            description=f"From {interaction.user}",
            timestamp=datetime.now(),
            color=discord.Color.blue()
        )
        embed.add_field(name="Type", value=self.type, inline=False)
        embed.add_field(name="Content", value=self.content, inline=False)
        await dev.send(embed=embed)

        embed = discord.Embed(
            title="전송 완료",
            description=f"`{self.type}`에 관한 연락이 전송되었습니다.\n이 메시지는 3초 후 삭제됩니다.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, delete_after=3)


class RedeemModal(ui.Modal, title='코드 등록'):
    code = ui.TextInput(label="코드", style=discord.TextStyle.short,
                        placeholder="여기에 코드를 입력해주세요", required=True, max_length=16)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        code = str(self.code)

        with open('database/codes.json') as file:
            codes = json.load(file)

        if code in codes:
            reward = codes[code]

            with open("database/codes.json", 'w') as file:
                del (codes[code])
                json.dump(codes, file, indent="\t",
                          ensure_ascii=False)

            with open('database/userdata.json') as file:
                userdata = json.load(file)

            if reward['rewardType'] == "PERIDOT":
                userdata[str(interaction.user.id)]["peridot"] = userdata[str(
                    interaction.user.id)]["peridot"] + reward['reward']

                peridot = format(int(reward['reward']), ',d')
                REWARD = f"{peridot} {PERIDOT_EMOJI}"

            elif reward['rewardType'] == "TOKEN":
                userdata[str(interaction.user.id)]["token"] = userdata[str(
                    interaction.user.id)]["token"] + reward['reward']

                token = format(int(reward['reward']), ',d')
                REWARD = f"{token} {TOKEN_EMOJI}"

            elif reward['rewardType'] == "ROLE":
                role = interaction.guild.get_role(reward['reward'])
                await interaction.user.add_roles(role)

                REWARD = f"<@&{reward['reward']}>"

            with open("database/userdata.json", 'w') as file:
                json.dump(userdata, file, indent="\t",
                          ensure_ascii=False)

            embed = discord.Embed(
                title="코드 등록 완료",
                description=f"코드를 성공적으로 등록했습니다.\n보상 종류: {reward['rewardTypeKR']}\n보상: {REWARD}",
                color=discord.Color.green()
            )
            await interaction.user.send(embed=embed)

            with open("config.json") as file:
                config = json.load(file)

            Log_channel = discord.utils.get(interaction.guild.channels,
                                            id=config["log_channel_id"])
            await Log_channel.send(embed=log.redeem(interaction.user.id, REWARD, code))
        else:
            embed = discord.Embed(
                title="코드 등록 실패",
                description=f"올바르지 않은 코드입니다.",
                color=discord.Color.red()
            )
            await interaction.user.send(embed=embed)

        embed = discord.Embed(
            title="코드 등록",
            description=f"DM을 확인해주세요.",
            color=discord.Color.blue()
        )
        return await interaction.response.send_message(embed=embed, delete_after=5)


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot
        self.active_pick = False
        self.picked_user_list = []
        self.last_pick = time.time()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 1070945112168861786:
            return
        if message.channel.id != 1070681870146224158:
            return
        if self.active_pick:
            return
        if time.time() - self.last_pick < 1800:
            return
        if random.randint(1, 100) >= 11:
            return
        self.active_pick = True
        self.picked_user_list = []

        embed = discord.Embed(
            title="PICK",
            description=f"땅에 {PERIDOT_EMOJI}가 떨어졌습니다.\n`/pick`을 입력하여 주워보세요!",
            color=discord.Color.blue()
        )
        msg = await message.channel.send(embed=embed)

        await asyncio.sleep(random.randint(10, 11))
        await msg.delete()

        self.active_pick = False
        self.last_pick = time.time()


    @commands.command(
        name="pick",
        description="떨어진 페리도트를 줍습니다."
    )
    async def pick(self, context: Context) -> None:
        await context.message.delete(delay=17)
        if self.active_pick:
            if context.author.id in self.picked_user_list:
                embed = discord.Embed(
                title="PICK",
                description=f"이미 페리도트를 주웠습니다!",
                color=discord.Color.red()
                )
                return await context.reply(embed=embed, delete_after=15)

            else:    
                with open("database/userdata.json", encoding="utf-8") as file:
                    userdata = json.load(file)

                picked_peridot = random.randint(0, 150)
                userdata[str(context.author.id)]["peridot"] = userdata[str(context.author.id)]["peridot"] + picked_peridot

                embed = discord.Embed(
                title="PICK",
                description=f"{context.author.mention}님이\n{picked_peridot} {PERIDOT_EMOJI}를 주웠습니다!",
                color=discord.Color.green()
                )
                await context.reply(embed=embed, delete_after=15)
                with open("database/userdata.json", 'w', encoding="utf-8") as file:
                    json.dump(userdata, file, indent="\t", ensure_ascii=False)

                self.picked_user_list.append(context.author.id)
        else:
            embed = discord.Embed(
                title="PICK",
                description=f"현재 활성화된 PICK이 없습니다!",
                color=discord.Color.red()
            )
            await context.reply(embed=embed, delete_after=15)
        
        

    @commands.command(
        name="ㅔㅑ차",                  
    )
    async def pick_typo(self, context: Context) -> None:
        picked_peridot = random.randint(100, 150)
        if self.active_pick:
            embed = discord.Embed(
                title="PICK",
                description=f"{context.author.mention}님이\n{picked_peridot} {PERIDOT_EMOJI}를 주울...수 있었지만\n오타를 내는 바람에 줍지 못했습니다.",
                color=discord.Color.green()
            )
            await context.send(embed=embed, delete_after=15)
        else:
            embed = discord.Embed(
                title="PICK",
                description=f"님아 진정하셈 아직 아님\n심지어 명렁어 그거 아님 ㅋㅋ",
                color=discord.Color.red()
            )
            await context.send(embed=embed, delete_after=15)

    @commands.hybrid_command(
        name="forcedrop",
        description="픽 강제드랍 (창조자 전용)"  
    )
    @checks.is_owner()
    async def forcedrop(self, context: Context) -> None:
        self.active_pick = True
        self.picked_user_list = []

        message_channel = context.guild.get_channel(1070681870146224158)

        embed = discord.Embed(
            title="PICK",
            description=f"땅에 {PERIDOT_EMOJI}가 떨어졌습니다.\n`/pick`을 입력하여 주워보세요!",
            color=discord.Color.blue()
        )
        msg = await message_channel.send(embed=embed)

        await context.send("PICK MESSAGE SENT")

        await asyncio.sleep(random.randint(10, 11))
        await msg.delete()

        self.active_pick = False
        self.last_pick = time.time()



    @commands.hybrid_command(
        name="help",
        description="실행 가능한 모든 커맨드를 표시합니다."
    )
    async def help(self, context: Context) -> None:
        prefix = self.bot.config["prefix"]
        embed = discord.Embed(
            title="Help", description="뱀샘봇의 커맨드들: ", color=discord.Color.purple())
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
    async def botinfo(self, context: Context) -> None:

        config = self.bot.config

        embed = discord.Embed(
            description=f"Dev By <@{424546094182039552}>",
            color=discord.Color.light_gray()
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner:",
            value="leejw0587",
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
    async def serverinfo(self, context: Context) -> None:
        roles = [role.name for role in context.guild.roles]
        if len(roles) > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title="**Server Name:**",
            description=f"{context.guild}",
            color=discord.Color.light_gray()
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
    async def ping(self, context: Context) -> None:
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=discord.Color.random()
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="attendance",
        description="출석 체크 커맨드입니다.",
    )
    async def attendance(self, context: Context) -> None:
        if context.channel.id != 1070685674178609213:
            embed = discord.Embed(
                title="Error!",
                description=f"<#1070685674178609213>에서만 이 명령어를 사용할 수 있습니다!",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        else:
            with open("database/userdata.json", encoding="utf-8") as file:
                userdata = json.load(file)
            with open('database/bpass_userdata.json', 'r') as file:
                bpUserdata = json.load(file)

            today = str(date.today())
            try:
                attendance_count = userdata[str(
                    context.author.id)]["attendance"]

                if userdata[str(context.author.id)]["last_attendance"] == today:
                    embed = discord.Embed(
                        title="Error!",
                        description=f"오늘({today})이미 출석을 했습니다!\n누적 출석 횟수: `{attendance_count}`회",
                        color=discord.Color.red()
                    )
                    await context.send(embed=embed)
                else:

                    reward = random.randint(1, 100)

                    userdata[str(context.author.id)]["last_attendance"] = today
                    userdata[str(context.author.id)]["attendance"] += 1
                    userdata[str(context.author.id)]["peridot"] = userdata[str(context.author.id)]["peridot"] + int(reward)
                    
                    isBspass = False
                    try:
                        bpUserdata[str(context.author.id)]["xp"] += 3600
                        isBspass = True
                    except:
                        pass

                    with open("database/userdata.json", 'w', encoding="utf-8") as file:
                        json.dump(userdata, file, indent="\t", ensure_ascii=False)
                    with open("database/bpass_userdata.json", 'w', encoding="utf-8") as file:
                        json.dump(bpUserdata, file, indent="\t", ensure_ascii=False)

                    attendance_count = userdata[str(context.author.id)]["attendance"]

                    # if isBspass:
                    #     embed = discord.Embed(
                    #         title="출석 완료!",
                    #         description=f"`{today}` 출석을 완료했습니다!\n누적 출석 횟수: `{attendance_count}`회\n**[출석 보상]**\n+ {reward} {PERIDOT_EMOJI}\n+ 3600 **bxp**",
                    #         color=discord.Color.blurple()
                    #     )
                    # else:
                    embed = discord.Embed(
                    title="출석 완료!",
                    description=f"`{today}` 출석을 완료했습니다!\n누적 출석 횟수: `{attendance_count}`회\n**[출석 보상]**\n+ {reward} {PERIDOT_EMOJI}",
                    color=discord.Color.blurple()
                    )

                    await context.send(embed=embed)

            except:
                embed = discord.Embed(
                    title="Error!",
                    description="유저를 찾을 수 없습니다.\n`/inventory`커맨드를 한 번 실행한 후 다시 시도해주세요.",
                    color=discord.Color.red()
                )
                await context.send(embed=embed)

    @commands.hybrid_command(
    name="createpc",
    description="개인 채널 생성 요청을 보냅니다."
    )
    @commands.has_role(1070680695258763305)
    @app_commands.describe(nickname="채널 주인의 한글 닉네임", channelname="채널 이름", genere="채널의 장르", description="채널 설명", restrictions="채널을 볼 수 있는 역할")
    async def createpc(self, context: Context, nickname: str, channelname: str, genere: str, description: str, restrictions: typing.Literal['모두', '인증', '변태', '그로테스크']):
        if context.channel.id == 1070686335498723439:
        # if context.channel.id == 958025710025453640: for dev server             
            admin_channel = context.guild.get_channel(1071266892993548298)
            # admin_channel = context.guild.get_channel(1062130045340110978) for dev server
            category = context.guild.get_channel(1070683365814050847)

            Check_RoleID = 1070680727009632297
            Pervert_RoleID = 1070680631450812467
            Grot_RoleID = 1070680559317160066

            buttons = CreatePcButtons()
            embed = discord.Embed(color=discord.Color.blue())
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
                embed = discord.Embed(color=discord.Color.green())
                embed.add_field(name="개인 채널 생성 요청",
                                value=f"개인 채널 생성 요청이 승인되었습니다.\n생성된 채널: <#{new_channel.id}>", inline=False)
                await respond.edit(content=" ", embed=embed)

            else:
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name="개인 채널 생성 요청",
                                value="개인 채널 생성 요청이 거부되었습니다.", inline=False)
                await respond.edit(content=" ", embed=embed)
            await req_message.delete()

        else:
            embed = discord.Embed(color=discord.Color.brand_red)
            embed.add_field(name="개인 채널 생성 요청",
                            value="해당 명령어는 <#706526566104170607> 에서만 작동합니다.", inline=False)
            await context.send(embed=embed)


    @commands.hybrid_command(
        name="reels",
        description="릴스를 보기 쉽게 보내줍니다."
    )
    @app_commands.describe(link="영상 링크")
    async def reels(self, context: Context, link: str):
        regexes_pre = [
            r'https:\/\/www\.instagram\.com\/reel\/([a-zA-Z0-9_\-]*)',
            # 'https:\/\/www\.tiktok\.com\/@[A-z]*\/video\/([a-zA-Z0-9_\-]*)',
            # 'https:\/\/www\.youtube\.com\/shorts\/([a-zA-Z0-9_\-]*)'
        ]

        regexes = []
        state = False
        hex = secrets.token_hex(nbytes=12)
        for s in regexes_pre:
            regexes.append(re.compile(s))

        await context.defer()

        def download(url, filename):
            opts = {
                'outtmpl': f'cogs/assets/Videos/{filename}.%(ext)s',
                # 'cookiefile': 'cookies.txt',
                'quiet': True,
                # 'format': '--all-formats'
            }

            with YoutubeDL(opts) as ytdl:
                ytdl.download([url])

            # Get filename (extension is unknown)
            path = glob.glob(f'cogs/assets/Videos/{filename}.*')[0]

            return path

        for regex in regexes:
            matches = re.search(regex, link)
            if matches:
                state = bool(matches)

        if state:
            # Download video
            path = download(link, hex)

            await context.send(file=discord.File(path))
            os.remove(path)

        else:
            await context.send(embed=embeds.EmbedRed("Error!", "릴스 링크만 지원합니다."))

    @commands.hybrid_command(
        name="report",
        description="개발자에게 익명으로 메시지를 보냅니다."
    )
    async def report(self, context: Context):
        await context.interaction.response.send_modal(ReportModal())

    @commands.hybrid_command(
        name='donate',
        description='개발자에게 후원할 수 있는 링크를 받습니다.'
    )
    async def donate(self, context: Context):
        embed = discord.Embed(
            title=":money_with_wings: DONATE",
            description=f"[여기](https://lnk.at/leejw0587)를 눌러 후원을 할 수 있어요.\n후원받은 금액은 뱀샘봇 개발 및 유지에 사용돼요.",
            color=discord.Color.brand_green()
        )
        await context.send(embed=embed)

    @commands.hybrid_group(
        name='code',
        description='선물 코드 관련 기능을 제공합니다.'
    )
    async def code(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                title="Error!",
                description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`redeem` - 코드를 등록합니다.\n`create` - 새로운 코드를 등록합니다.\n`remove` - 등록된 코드를 제거합니다.\n`list` - 등록된 코드를 확인합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @code.command(
        name="redeem",
        description="코드를 등록합니다.",
    )
    async def code_redeem(self, context: Context):
        await context.interaction.response.send_modal(RedeemModal())

    @code.command(
        name='create',
        description='새로운 코드를 생성합니다. (창조자 전용)'
    )
    @app_commands.describe(code="커스텀 코드 또는 'RANDOM'", type="보상 종류", reward="주어질 보상")
    @checks.is_owner()
    async def code_create(self, context: Context, code: str, type: typing.Literal['페리도트', '토큰', '역할'], reward: str):
        with open('database/codes.json') as file:
            codes = json.load(file)
        if code == 'RANDOM':
            char = string.ascii_uppercase + string.digits
            code = ''.join(random.choice(char) for x in range(16))

        if type == '페리도트':
            rewardType = "PERIDOT"
            rewardStr = f"{format(int(reward), ',d')} {PERIDOT_EMOJI}"
        elif type == '토큰':
            rewardType = "TOKEN"
            rewardStr = f"{format(int(reward), ',d')} {TOKEN_EMOJI}"
        elif type == '역할':
            rewardType = "ROLE"
            rewardStr = f"<@&{reward}>"

        newCode = {
            code: {
                "code": code,
                "rewardType": rewardType,
                "rewardTypeKR": type,
                "reward": int(reward)
            }
        }

        codes.update(newCode)

        with open("database/codes.json", 'w') as file:
            json.dump(codes, file, indent="\t",
                      ensure_ascii=False)

        await context.send(embed=embeds.EmbedBlurple("코드 생성", f"새로운 코드를 생성했습니다.\n코드: `{code}`\n보상 종류: `{type}`\n보상: {rewardStr}"))

    @code.command(
        name='remove',
        description='생성된 코드를 삭제합니다. (창조자 전용)'
    )
    @app_commands.describe(code="삭제할 코드")
    @checks.is_owner()
    async def code_remove(self, context: Context, code: str):
        with open('database/codes.json') as file:
            codes = json.load(file)

        if code in codes:
            with open("database/codes.json", 'w') as file:
                del (codes[code])
                json.dump(codes, file, indent="\t",
                          ensure_ascii=False)
            embed = discord.Embed(
                title="코드",
                description=f"`{code}`를 삭제했습니다.",
                color=discord.Color.orange()
            )
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="코드",
                description=f"존재하지 않는 코드입니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return

    @code.command(
        name='list',
        description='생성된 코드의 목록을 보여줍니다. (창조자 전용)'
    )
    @checks.is_owner()
    async def code_list(self, context: Context):
        with open('database/codes.json') as file:
            codes = json.load(file)

        embed = discord.Embed(
            title="코드",
            description="< 사용 가능한 코드 목록 >",
            color=discord.Color.brand_green()
        )
        for i in codes:
            CODE = codes[i]['code']
            REWARDTYPEKR = codes[i]['rewardTypeKR']
            REWARDTYPE = codes[i]['rewardType']

            if REWARDTYPE == "PERIDOT":
                REWARD = f"{format(int(codes[i]['reward']), ',d')} {PERIDOT_EMOJI}"

            elif REWARDTYPE == "TOKEN":
                REWARD = f"{format(int(codes[i]['reward']), ',d')} {TOKEN_EMOJI}"

            elif REWARDTYPE == "ROLE":
                REWARD = f"<@&{codes[i]['reward']}>"

            embed.add_field(
                name=f"`{CODE}`",
                value=f"보상 종류: `{REWARDTYPEKR}`\n보상: {REWARD}",
                inline=False
            )

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="invite",
        description="뱀샘크루의 초대 링크를 보내줍니다."
    )
    async def invite(self, context: Context):
        embed = discord.Embed(
            title="초대 링크",
            description=f"https://discord.gg/2sPgEZcMTv",
            color=0x9C84EF
        )
        await context.send(embed=embed)     


    @commands.hybrid_command(
        name="db_init",
        description="dev"
    )
    @checks.is_dev()
    async def db_init(self ,context: Context):
        with open("database/leaderboard.json", encoding="utf-8") as file:
            leaderboard = json.load(file)
        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)

        context.defer()

        for user in context.guild.members:
            if str(user.id) in userdata:
                pass
            else:
                newUser = {
                    str(user.id): {
                        "username": user.display_name,
                        "userid": str(user.id),
                        "xp": userdata[str(user.id)]["xp"],
                        "level": userdata[str(user.id)]["level"],
                    }
                }
                leaderboard.update(newUser)
                with open("database/leaderboard.json", 'w', encoding="utf-8") as file:
                    json.dump(leaderboard, file, indent="\t", ensure_ascii=False)

        context.send("Done")


async def setup(bot):
    await bot.add_cog(General(bot))
