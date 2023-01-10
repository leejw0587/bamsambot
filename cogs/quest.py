import discord
import json

from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands

from helpers import checks, log

PERIDOT_EMOJI = "<:peridot:722474684045721973>"
TOKEN_EMOJI = "<:token:884035217252311051>"

global QUEST_STATE
global QUEST_ANSWER_LIST
global QUEST_REWARDS

QUEST_STATE = False
QUEST_ANSWER_LIST = []
QUEST_REWARDS = {
    "PERIDOT": 0,
    "TOKEN": 0,
    "ROLEID": None
}


class Quest(commands.Cog, name="quest"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(
        name="quest",
        description="퀘스트 관련 커맨드를 제공합니다.",
    )
    async def quest(self, context: Context) -> None:
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                title="Error!",
                description="Subcommand를 작성해주세요. \n\n**Subcommands:**\n`answer` - 퀘스트 정답을 제출합니다.\n`addanswer` - 정답을 추가합니다.\n`removeanswer` - 정답을 제거합니다.\n`setreward` - 보상을 설정합니다.\n`resetreward` - 보상을 초기화합니다.\n`init` - 퀘스트를 초기화합니다.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @quest.command(
        name="answer",
        description="퀘스트 정답을 제출합니다.",
    )
    @app_commands.describe(answer="제출할 정답")
    async def quest_answer(self, context: Context, answer: str) -> None:
        global QUEST_STATE
        global QUEST_ANSWER_LIST
        global QUEST_REWARDS
        if QUEST_STATE == True:
            if answer in QUEST_ANSWER_LIST:

                embed = discord.Embed(
                    title="정답!", description="정답입니다!", color=0x57c179)
                embed.add_field(
                    name="보상", value=f"{QUEST_REWARDS['PERIDOT']} {PERIDOT_EMOJI}\n{QUEST_REWARDS['TOKEN']} {TOKEN_EMOJI}\n<@&{QUEST_REWARDS['ROLEID']}>", inline=False)
                await context.send(embed=embed)

                with open("database/userdata.json", encoding="utf-8") as file:
                    userdata = json.load(file)
                userdata[str(context.author.id)]["peridot"] = userdata[str(
                    context.author.id)]["peridot"] + int(QUEST_REWARDS['PERIDOT'])
                userdata[str(context.author.id)]["token"] = userdata[str(
                    context.author.id)]["token"] + int(QUEST_REWARDS['TOKEN'])
                if QUEST_REWARDS["ROLEID"] is not None:
                    role = context.guild.get_role(int(QUEST_REWARDS["ROLEID"]))
                    await context.author.add_roles(role)
                with open("database/userdata.json", 'w', encoding="utf-8") as file:
                    json.dump(userdata, file, indent="\t", ensure_ascii=False)

                QUEST_STATE = False

                Log_channel = discord.utils.get(context.guild.channels,
                                                id=self.bot.config["log_channel_id"])
                await Log_channel.send(log.got_answer(context))
        else:
            embed = discord.Embed(
                title="Error!",
                description="현재 활성화된 퀘스트가 없습니다.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @quest.command(
        name="addanswer",
        description="퀘스트 정답을 추가합니다. (창조자 전용)"
    )
    @app_commands.describe(answer="추가할 정답")
    @checks.is_owner()
    async def quest_addanswer(self, context: Context, answer: str) -> None:
        global QUEST_STATE
        global QUEST_ANSWER_LIST
        global QUEST_REWARDS

        QUEST_ANSWER_LIST.append(answer)
        embed = discord.Embed(
            title="정답 추가 완료",
            description=f"정답 `{answer}`(을)를 성공적으로 추가했습니다.\n등록된 정답: {QUEST_ANSWER_LIST}",
            color=0x4BB543
        )
        await context.send(embed=embed)

    @quest.command(
        name="removeanswer",
        description="퀘스트 정답을 제거합니다. (창조자 전용)"
    )
    @app_commands.describe(answer="제거할 정답")
    @checks.is_owner()
    async def quest_removeanswer(self, context: Context, answer: str) -> None:
        global QUEST_STATE
        global QUEST_ANSWER_LIST
        global QUEST_REWARDS

        if answer in QUEST_ANSWER_LIST:
            QUEST_ANSWER_LIST.remove(answer)
            embed = discord.Embed(
                title="정답 제거 완료",
                description=f"정답 `{answer}`(을)를 성공적으로 제거했습니다.\n등록된 정답: {QUEST_ANSWER_LIST}",
                color=0x4BB543
            )
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="정답 리스트에 등록되지 않은 정답입니다.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @quest.command(
        name="setreward",
        description="퀘스트 보상을 설정합니다. (창조자 전용)"
    )
    @app_commands.describe(peridot="페리도트", token="토큰", role="역할")
    @checks.is_owner()
    async def quest_setreward(self, context: Context, peridot: int, token: int, role: discord.Role = None) -> None:
        global QUEST_STATE
        global QUEST_ANSWER_LIST
        global QUEST_REWARDS

        QUEST_REWARDS["PERIDOT"] = peridot
        QUEST_REWARDS["TOKEN"] = token
        QUEST_REWARDS["ROLEID"] = role.id

        embed = discord.Embed(
            title="보상 등록 완료",
            description=f"보상을 성공적으로 등록하였습니다",
            color=0x4BB543
        )
        await context.send(embed=embed)

    @quest.command(
        name="resetreward",
        description="퀘스트 보상을 초기화합니다. (창조자 전용)"
    )
    @checks.is_owner()
    async def quest_resetreward(self, context: Context) -> None:
        global QUEST_STATE
        global QUEST_ANSWER_LIST
        global QUEST_REWARDS

        QUEST_REWARDS["PERIDOT"] = 0
        QUEST_REWARDS["TOKEN"] = 0
        QUEST_REWARDS["ROLEID"] = 0

        embed = discord.Embed(
            title="보상 초기화 완료",
            description=f"보상을 성공적으로 초기화하였습니다",
            color=0x4BB543
        )
        await context.send(embed=embed)

    @quest.command(
        name="setstate",
        description="퀘스트 상태를 설정합니다. (창조자 전용)"
    )
    @checks.is_owner()
    async def quest_setstate(self, context: Context, state: bool) -> None:
        global QUEST_STATE
        global QUEST_ANSWER_LIST
        global QUEST_REWARDS

        QUEST_STATE = state

        embed = discord.Embed(
            title="퀘스트 상태 변경 완료",
            description=f"현재 퀘스트 상태: {QUEST_STATE}",
            color=0x4BB543
        )
        await context.send(embed=embed)

    @quest.command(
        name="info",
        description="퀘스트 관련 정보를 모두 표시합니다. (창조자 전용)"
    )
    @checks.is_owner()
    async def quest_info(self, context: Context) -> None:
        global QUEST_STATE
        global QUEST_ANSWER_LIST
        global QUEST_REWARDS

        embed = discord.Embed(
            title="퀘스트 정보",
            description=f"퀘스트 상태: {QUEST_STATE}\n정답 목록: {QUEST_ANSWER_LIST}\n[보상]\n{QUEST_REWARDS['PERIDOT']} {PERIDOT_EMOJI}\n{QUEST_REWARDS['TOKEN']} {TOKEN_EMOJI}\n<@&{QUEST_REWARDS['ROLEID']}>",
            color=0x4BB543
        )
        await context.send(embed=embed)

    @quest.command(
        name="init",
        description="퀘스트를 초기화합니다. (창조자 전용)"
    )
    @checks.is_owner()
    async def quest_init(self, context: Context) -> None:
        global QUEST_STATE
        global QUEST_ANSWER_LIST
        global QUEST_REWARDS

        QUEST_STATE = False
        QUEST_ANSWER_LIST = []
        QUEST_REWARDS["PERIDOT"] = 0
        QUEST_REWARDS["TOKEN"] = 0
        QUEST_REWARDS["ROLEID"] = 0

        embed = discord.Embed(
            title="초기화 완료",
            description=f"퀘스트를 성공적으로 초기화하였습니다.",
            color=0x4BB543
        )
        await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Quest(bot))
