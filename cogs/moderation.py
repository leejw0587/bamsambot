import discord
import chat_exporter
import io
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, db_manager, log


class Moderation(commands.Cog, name="moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="nick",
        description="유저의 닉네임을 뱀샘크루에 맞게 변경합니다. (창조자 전용)",
    )
    @checks.is_owner()
    @app_commands.describe(user="대상 유저", nickname="변경할 닉네임")
    async def nick(self, context: Context, user: discord.User, *, nickname: str = None) -> None:
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        nickname = "༺ৡۣۜ͜ ৡ " + nickname + " ৡۣۜ͜ ৡ༻"
        try:
            await member.edit(nick=nickname)
            embed = discord.Embed(
                title="닉네임 변경 완료!",
                description=f"`{member}`의 닉네임을 `{nickname}`(으)로 설정하였습니다!",
                color=discord.Color.green()
            )
            await context.send(embed=embed)
        except:
            embed = discord.Embed(
                title="Error!",
                description="오류가 발생하였습니다. 다시 시도해주세요.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @commands.hybrid_group(
        name="warning",
        description="유저의 경고를 관리합니다. (창조자 전용)",
    )
    @checks.is_informant()
    @checks.not_blacklisted()
    async def warning(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                title="Error!",
                description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`add` - 유저에게 경고를 추가합니다.\n`remove` - 유저로부터 경고를 제거합니다.\n`list` - 유저의 모든 경고를 확인합니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @warning.command(
        name="add",
        description="유저에게 경고를 추가합니다. (창조자 전용)",
    )
    @checks.not_blacklisted()
    @checks.is_informant()
    @app_commands.describe(user="대상 유저", reason="경고 사유")
    async def warning_add(self, context: Context, user: discord.User, *, reason: str = "명시되지 않음") -> None:
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        total = await db_manager.add_warn(
            user.id, context.guild.id, context.author.id, reason)
        embed = discord.Embed(
            title="경고",
            description=f"**{member}**(이)가 경고를 받았습니다!\n누적 경고: {total}",
            color=discord.Color.red()
        )
        embed.add_field(
            name="사유:",
            value=reason
        )
        await context.send(embed=embed)
        try:
            embed = discord.Embed(
                title="경고를 받았습니다!",
                description=f"경고 사유: ``{reason}``\n누적 경고: {total}회",
                color=discord.Color.red()
            )
            await member.send(embed=embed)
        except:
            # Couldn't send a message in the private messages of the user
            embed = discord.Embed(
                title=f"{member.name}이(가) 경고를 받았습니다!",
                description=f"경고 사유: ``{reason}``",
                color=discord.Color.red()
            )
            await member.send(embed=embed)
        Log_channel = discord.utils.get(context.guild.channels,
                                        id=self.bot.config["log_channel_id"])
        await Log_channel.send(log.warning("add", context, user))

    @warning.command(
        name="remove",
        description="유저의 경고를 제거합니다. (창조자 전용)",
    )
    @checks.not_blacklisted()
    @checks.is_informant()
    @app_commands.describe(user="대상 유저", warn_id="제거할 경고ID")
    async def warning_remove(self, context: Context, user: discord.User, warn_id: int) -> None:
        member = context.guild.get_member(user.id) or await context.guild.fetch_member(user.id)
        total = await db_manager.remove_warn(warn_id, user.id, context.guild.id)
        embed = discord.Embed(
            title="경고 제거",
            description=f"**{member}** 에게 부여된 경고ID **#{warn_id}** 를 제거했습니다!\n누적 경고: {total}",
            color=discord.Color.orange()
        )
        await context.send(embed=embed)

        Log_channel = discord.utils.get(context.guild.channels,
                                        id=self.bot.config["log_channel_id"])
        await Log_channel.send(log.warning("remov", context, user))

    @warning.command(
        name="list",
        description="유저의 경고 목록을 나타냅니다. (창조자 전용)",
    )
    @checks.is_informant()
    @checks.not_blacklisted()
    @app_commands.describe(user="대상 유저")
    async def warning_list(self, context: Context, user: discord.User):
        warnings_list = await db_manager.get_warnings(user.id, context.guild.id)
        embed = discord.Embed(
            title=f"{user}의 경고 목록",
            color=discord.Color.orange()
        )
        description = ""
        if len(warnings_list) == 0:
            description = "이 유저는 경고를 받지 않았습니다."
        else:
            for warning in warnings_list:
                description += f"• <@{warning[2]}>: **{warning[3]}** (<t:{warning[4]}>) - 경고ID #{warning[5]}\n"
        embed.description = description
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="purge",
        description="메시지를 청소합니다. (창조자 전용)"
    )
    @checks.is_owner()
    async def purge(self, context: Context, amount: int):
        await context.send(f"`{amount}`개의 메시지를 삭제합니다...", delete_after=5)
        await context.channel.purge(limit=amount+1)

        Log_channel = discord.utils.get(context.guild.channels,
                                        id=self.bot.config["log_channel_id"])
        await Log_channel.send(log.purge(context, amount))

    @commands.hybrid_command(
        name="transcript",
        description="채팅창의 transcript를 생성합니다. (창조자 전용)"
    )
    @checks.is_owner()
    async def transcript(self, context: Context, channel: discord.TextChannel):
        # await context.defer()
        # transcript = await chat_exporter.export(channel)

        # if transcript is None:
        #     return

        # transcript_file = discord.File(
        #     io.BytesIO(transcript.encode()),
        #     filename=f"transcript-{channel.name}.html",
        # )

        # message = await context.send(file=transcript_file)
        # link = await chat_exporter.link(message)

        # await context.send("Click this link to view the transcript online: " + link)

        await context.defer()
        transcript = await chat_exporter.export(channel, tz_info="Asia/Seoul", bot=self.bot)

        with open("cogs/assets/Transcripts/" + str(channel.id) + ".html", "w") as file:
            file.write(str(transcript))

        transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                       filename=f"{str(channel.id)}.html")

        await context.send(file=transcript_file)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
