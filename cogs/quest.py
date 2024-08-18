import discord
import json
import typing

from discord.ext import commands
from discord.ext.commands import Context
from discord import app_commands, ui

from helpers import checks, log

PERIDOT_EMOJI = "<:peridot:722474684045721973>"
TOKEN_EMOJI = "<:token:884035217252311051>"


class QuestAnswerModal(ui.Modal, title='정답 제출'):
    answer = ui.TextInput(label="여기에 정답을 입력해주세요",
                          style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        with open("config.json") as file:
            config = json.load(file)

        with open("database/quest.json") as file:
            quest = json.load(file)

        ANSWER = str(self.answer)
        ACTIVEQUEST = quest["__ACTIVE_QUEST"]
        QUEST_ANSWER_LIST = list(quest[ACTIVEQUEST]["answer"])
        QUEST_REWARD_PERIDOT = quest[ACTIVEQUEST]["peridot"]
        QUEST_REWARD_TOKEN = quest[ACTIVEQUEST]["token"]
        QUEST_REWARD_ROLE = quest[ACTIVEQUEST]["roleid"]
        if QUEST_REWARD_ROLE == None:
            DISPLAYROLE = "역할 없음"
        else:
            DISPLAYROLE = f"<@&{QUEST_REWARD_ROLE}>"
        user = interaction.user
        guild = interaction.guild
        Log_channel = guild.get_channel(config["log_channel_id"])

        embed = discord.Embed(
            title="정답 제출 완료",
            description=f"DM을 확인해주세요.",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed)

        if ANSWER in QUEST_ANSWER_LIST:
            embed = discord.Embed(
                title="정답!", description="정답입니다!", color=discord.Color.green())
            embed.add_field(
                name="보상 목록", value=f"{QUEST_REWARD_PERIDOT} {PERIDOT_EMOJI}\n{QUEST_REWARD_TOKEN} {TOKEN_EMOJI}\n{DISPLAYROLE}", inline=False)
            await user.send(embed=embed)

            with open("database/userdata.json", encoding="utf-8") as file:
                userdata = json.load(file)
            userdata[str(user.id)]["peridot"] = userdata[str(
                user.id)]["peridot"] + int(QUEST_REWARD_PERIDOT)
            userdata[str(user.id)]["token"] = userdata[str(
                user.id)]["token"] + int(QUEST_REWARD_TOKEN)
            if QUEST_REWARD_ROLE is not None:
                role = guild.get_role(int(QUEST_REWARD_ROLE))
                await user.add_roles(role)
            with open("database/userdata.json", 'w', encoding="utf-8") as file:
                json.dump(userdata, file, indent="\t", ensure_ascii=False)

            await Log_channel.send(log.got_answer(user.id))

            quest["__ACTIVE_QUEST"] = None
            with open("database/quest.json", 'w', encoding="utf-8") as file:
                json.dump(quest, file, indent="\t", ensure_ascii=False)
        else:
            embed = discord.Embed(
                title="오답!",
                description=f"오답입니다.\n입력한 답: `{self.answer}`",
                color=discord.Color.red()
            )
            await user.send(embed=embed)

class ProtocolModal(ui.Modal, title='Protocol'):
    answer = ui.TextInput(label="SYSTEM?/ROOT:",
                          style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        answer = str(self.answer)
        user = interaction.user
        
        
        if answer == "gettool":
            await user.send(file=discord.File("database/rubytool.exe"))
        else:
            await user.send("Error.")

        await interaction.response.send_message(".", delete_after=1)


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
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @quest.command(
        name="answer",
        description="퀘스트 정답을 제출합니다.",
    )
    async def quest_answer(self, context: Context) -> None:
        with open("database/quest.json") as file:
            quest = json.load(file)

        if quest["__ACTIVE_QUEST"] != None:
            await context.interaction.response.send_modal(QuestAnswerModal())
        else:
            embed = discord.Embed(
                title="Error!",
                description="현재 활성화된 퀘스트가 없습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)

    @quest.command(
        name="view",
        description="퀘스트 목록을 확인합니다. (창조자 전용)"
    )
    @app_commands.describe()
    @checks.is_owner()
    async def quest_view(self, context: Context) -> None:
        with open("database/quest.json") as file:
            quest = json.load(file)

        active_quest = quest["__ACTIVE_QUEST"]

        embed = discord.Embed(
            title="퀘스트 목록", description=f"활성화된 퀘스트: {active_quest}", color=discord.Color.blue())
        for i in quest:
            if i == "__ACTIVE_QUEST":
                pass
            else:
                questname = quest[i]["name"]
                answer = quest[i]["answer"]
                peridot = quest[i]["peridot"]
                token = quest[i]["token"]
                role = quest[i]["roleid"]
                rolemention = None
                if role != None:
                    rolemention = f"<@&{role}>"
                embed.add_field(
                    name=f"{questname}", value=f"정답: {answer}\n페리도트: {peridot}\n토큰: {token}\n역할: {rolemention}", inline=False)
        await context.send(embed=embed)

    @quest.command(
        name="new",
        description="새로운 퀘스트를 생성합니다. (창조자 전용)"
    )
    @app_commands.describe(name="퀘스트 이름")
    @checks.is_owner()
    async def quest_new(self, context: Context, name: str) -> None:
        with open("database/quest.json") as file:
            quest = json.load(file)

        newQuest = {
            name: {
                "name": name,
                "answer": [],
                "peridot": 0,
                "token": 0,
                "roleid": None
            }
        }

        quest.update(newQuest)
        with open("database/quest.json", 'w') as file:
            json.dump(quest, file, indent="\t",
                      ensure_ascii=False)

        embed = discord.Embed(
            title="퀘스트 생성 완료",
            description=f"새로운 퀘스트를 생성했습니다: `{name}`",
            color=discord.Color.green()
        )
        await context.send(embed=embed)

    @quest.command(
        name="remove",
        description="퀘스트를 제거합니다. (창조자 전용)"
    )
    @app_commands.describe(name="퀘스트 이름")
    @checks.is_owner()
    async def quest_remove(self, context: Context, name: str) -> None:
        with open("database/quest.json") as file:
            quest = json.load(file)
        if name not in quest:
            embed = discord.Embed(
                title="Error!",
                description=f"퀘스트가 존재하지 않습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        else:
            del (quest[name])
            with open("database/quest.json", 'w') as file:
                json.dump(quest, file, indent="\t",
                          ensure_ascii=False)
            embed = discord.Embed(
                title="퀘스트 제거 완료",
                description=f"`{name}`을(를) 제거했습니다.",
                color=discord.Color.green()
            )
            await context.send(embed=embed)

    @quest.command(
        name="activate",
        description="퀘스트를 활성화합니다. (창조자 전용)"
    )
    @app_commands.describe(name="퀘스트 이름")
    @checks.is_owner()
    async def quest_activate(self, context: Context, name: str) -> None:
        with open("database/quest.json") as file:
            quest = json.load(file)
        if name not in quest:
            embed = discord.Embed(
                title="Error!",
                description=f"퀘스트가 존재하지 않습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        else:
            quest["__ACTIVE_QUEST"] = name
            with open("database/quest.json", 'w', encoding="utf-8") as file:
                json.dump(quest, file, indent="\t", ensure_ascii=False)
            embed = discord.Embed(
                title="퀘스트 활성화",
                description=f"{name}을(를) 활성화하였습니다.",
                color=discord.Color.green()
            )
            await context.send(embed=embed)

    @quest.command(
        name="deactivate",
        description="퀘스트를 비활성화합니다. (창조자 전용)"
    )
    @checks.is_owner()
    async def quest_deactivate(self, context: Context) -> None:
        with open("database/quest.json") as file:
            quest = json.load(file)

        quest["__ACTIVE_QUEST"] = None
        with open("database/quest.json", 'w', encoding="utf-8") as file:
            json.dump(quest, file, indent="\t", ensure_ascii=False)
        embed = discord.Embed(
            title="퀘스트 비활성화",
            description=f"퀘스트를 비활성화하였습니다.",
            color=discord.Color.orange()
        )
        await context.send(embed=embed)

    @quest.command(
        name="modify",
        description="퀘스트를 수정합니다. (창조자 전용)"
    )
    @app_commands.describe(name="퀘스트 이름", key="수정할 대상", value="수정할 값")
    @checks.is_owner()
    async def quest_active(self, context: Context, name: str, key: typing.Literal['정답', '페리도트', '토큰', '역할'], value: str = None) -> None:
        with open("database/quest.json") as file:
            quest = json.load(file)

        if name not in quest:
            embed = discord.Embed(
                title="Error!",
                description=f"퀘스트가 존재하지 않습니다.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
        else:
            if key == "정답":
                value = value.split(',')
                quest[name]["answer"] = value
            elif key == "페리도트":
                quest[name]["peridot"] = int(value)
            elif key == "토큰":
                quest[name]["token"] = int(value)
            elif key == "역할":
                quest[name]["roleid"] = int(value)
            else:
                embed = discord.Embed(
                    title="Key Error!",
                    description=f"`정답/페리도트/토큰/역할`중 하나를 선택해주세요",
                    color=discord.Color.red()
                )
                await context.send(embed=embed)
                return

            with open("database/quest.json", 'w', encoding="utf-8") as file:
                json.dump(quest, file, indent="\t", ensure_ascii=False)

            embed = discord.Embed(
                title="퀘스트 수정",
                description=f"{name}의 {key}을(를) {value}(으)로 설정하였습니다.",
                color=discord.Color.blurple()
            )
            await context.send(embed=embed)

    # @quest.command(
    #     name="addanswer",
    #     description="퀘스트 정답을 추가합니다. (창조자 전용)"
    # )
    # @app_commands.describe(answer="추가할 정답")
    # @checks.is_owner()
    # async def quest_addanswer(self, context: Context, answer: str) -> None:
    #     global QUEST_STATE
    #     global QUEST_ANSWER_LIST
    #     global QUEST_REWARDS

    #     QUEST_ANSWER_LIST.append(answer)
    #     embed = discord.Embed(
    #         title="정답 추가 완료",
    #         description=f"정답 `{answer}`(을)를 성공적으로 추가했습니다.\n등록된 정답: {QUEST_ANSWER_LIST}",
    #         color=0x4BB543
    #     )
    #     await context.send(embed=embed)

    # @quest.command(
    #     name="removeanswer",
    #     description="퀘스트 정답을 제거합니다. (창조자 전용)"
    # )
    # @app_commands.describe(answer="제거할 정답")
    # @checks.is_owner()
    # async def quest_removeanswer(self, context: Context, answer: str) -> None:
    #     global QUEST_STATE
    #     global QUEST_ANSWER_LIST
    #     global QUEST_REWARDS

    #     if answer in QUEST_ANSWER_LIST:
    #         QUEST_ANSWER_LIST.remove(answer)
    #         embed = discord.Embed(
    #             title="정답 제거 완료",
    #             description=f"정답 `{answer}`(을)를 성공적으로 제거했습니다.\n등록된 정답: {QUEST_ANSWER_LIST}",
    #             color=0x4BB543
    #         )
    #         await context.send(embed=embed)
    #     else:
    #         embed = discord.Embed(
    #             title="Error!",
    #             description="정답 리스트에 등록되지 않은 정답입니다.",
    #             color=0xE02B2B
    #         )
    #         await context.send(embed=embed)

    # @quest.command(
    #     name="setreward",
    #     description="퀘스트 보상을 설정합니다. (창조자 전용)"
    # )
    # @app_commands.describe(peridot="페리도트", token="토큰", role="역할")
    # @checks.is_owner()
    # async def quest_setreward(self, context: Context, peridot: int, token: int, role: discord.Role = None) -> None:
    #     global QUEST_STATE
    #     global QUEST_ANSWER_LIST
    #     global QUEST_REWARDS

    #     QUEST_REWARDS["PERIDOT"] = peridot
    #     QUEST_REWARDS["TOKEN"] = token
    #     QUEST_REWARDS["ROLEID"] = role.id

    #     embed = discord.Embed(
    #         title="보상 등록 완료",
    #         description=f"보상을 성공적으로 등록하였습니다",
    #         color=0x4BB543
    #     )
    #     await context.send(embed=embed)

    # @quest.command(
    #     name="resetreward",
    #     description="퀘스트 보상을 초기화합니다. (창조자 전용)"
    # )
    # @checks.is_owner()
    # async def quest_resetreward(self, context: Context) -> None:
    #     global QUEST_STATE
    #     global QUEST_ANSWER_LIST
    #     global QUEST_REWARDS

    #     QUEST_REWARDS["PERIDOT"] = 0
    #     QUEST_REWARDS["TOKEN"] = 0
    #     QUEST_REWARDS["ROLEID"] = 0

    #     embed = discord.Embed(
    #         title="보상 초기화 완료",
    #         description=f"보상을 성공적으로 초기화하였습니다",
    #         color=0x4BB543
    #     )
    #     await context.send(embed=embed)

    # @quest.command(
    #     name="setstate",
    #     description="퀘스트 상태를 설정합니다. (창조자 전용)"
    # )
    # @checks.is_owner()
    # async def quest_setstate(self, context: Context, state: bool) -> None:
    #     global QUEST_STATE
    #     global QUEST_ANSWER_LIST
    #     global QUEST_REWARDS

    #     QUEST_STATE = state

    #     embed = discord.Embed(
    #         title="퀘스트 상태 변경 완료",
    #         description=f"현재 퀘스트 상태: {QUEST_STATE}",
    #         color=0x4BB543
    #     )
    #     await context.send(embed=embed)

    # @quest.command(
    #     name="info",
    #     description="퀘스트 관련 정보를 모두 표시합니다. (창조자 전용)"
    # )
    # @checks.is_owner()
    # async def quest_info(self, context: Context) -> None:
    #     global QUEST_STATE
    #     global QUEST_ANSWER_LIST
    #     global QUEST_REWARDS

    #     embed = discord.Embed(
    #         title="퀘스트 정보",
    #         description=f"퀘스트 상태: {QUEST_STATE}\n정답 목록: {QUEST_ANSWER_LIST}\n[보상]\n{QUEST_REWARDS['PERIDOT']} {PERIDOT_EMOJI}\n{QUEST_REWARDS['TOKEN']} {TOKEN_EMOJI}\n<@&{QUEST_REWARDS['ROLEID']}>",
    #         color=0x4BB543
    #     )
    #     await context.send(embed=embed)

    # @quest.command(
    #     name="init",
    #     description="퀘스트를 초기화합니다. (창조자 전용)"
    # )
    # @checks.is_owner()
    # async def quest_init(self, context: Context) -> None:
    #     global QUEST_STATE
    #     global QUEST_ANSWER_LIST
    #     global QUEST_REWARDS

    #     QUEST_STATE = False
    #     QUEST_ANSWER_LIST = []
    #     QUEST_REWARDS["PERIDOT"] = 0
    #     QUEST_REWARDS["TOKEN"] = 0
    #     QUEST_REWARDS["ROLEID"] = 0

    #     embed = discord.Embed(
    #         title="초기화 완료",
    #         description=f"퀘스트를 성공적으로 초기화하였습니다.",
    #         color=0x4BB543
    #     )
    #     await context.send(embed=embed)

    @commands.hybrid_command(
        name="protocol",
        description="backdoor",
    )
    async def protocol(self, context: Context) -> None:
        await context.interaction.response.send_modal(ProtocolModal())

async def setup(bot):
    await bot.add_cog(Quest(bot))
