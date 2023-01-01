import discord
import json
from discord import app_commands, Interaction, Object, InteractionResponse
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, log


class SelectProblem(discord.ui.Select):
    def __init__(self):
        options = [  # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="질문",
                description="질문이 있을 때 선택해주세요",
                emoji="❔"
            ),
            discord.SelectOption(
                label="지원",
                description="기술적 지원이 필요할 때 선택해주세요",
                emoji="🔧"
            ),
            discord.SelectOption(
                label="신고",
                description="유저를 신고할 때 선택해주세요",
                emoji="🚫"
            ),
        ]
        super().__init__(
            placeholder="현재 문제 상황을 선택해주세요",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):

        with open("database/ticket.json") as file:
            ticket_json = json.load(file)
        with open("config.json") as file:
            config = json.load(file)

        user = interaction.user
        guild = interaction.guild
        creator = guild.get_role(int(ticket_json["creator_role_id"]))
        log_channel = guild.get_channel(config["log_channel_id"])

        if self.values[0] == "질문":
            new_channel = await guild.create_text_channel(name=f'❔┃{user}-ticket')
        elif self.values[0] == "지원":
            new_channel = await guild.create_text_channel(name=f'🔧┃{user}-ticket')
        elif self.values[0] == "신고":
            new_channel = await guild.create_text_channel(name=f'🚫┃{user}-ticket')

        await new_channel.set_permissions(guild.get_role(guild.id),
                                          send_messages=False,
                                          read_messages=False)
        await new_channel.set_permissions(user,
                                          send_messages=True,
                                          read_messages=True,
                                          add_reactions=True,
                                          embed_links=True,
                                          attach_files=True,
                                          read_message_history=True,
                                          external_emojis=True)
        await new_channel.set_permissions(creator,
                                          send_messages=True,
                                          read_messages=True,
                                          add_reactions=True,
                                          embed_links=True,
                                          attach_files=True,
                                          read_message_history=True,
                                          external_emojis=True,
                                          manage_messages=True)
        await new_channel.send(f"<@&{creator.id}>")
        embed = discord.Embed(color=0x9C84EF)
        embed.add_field(
            name=f"새로운 티켓 - {user}", value="곧 어드민이 도착할 예정입니다. 잠시만 기다려주세요.", inline=False)
        await new_channel.send(embed=embed)

        ticket_json["ticket_channel_ids"].append(new_channel.id)

        with open("database/ticket.json", 'w') as file:
            json.dump(ticket_json, file, indent="\t", ensure_ascii=False)

        await interaction.response.edit_message(content=f'``{self.values[0]}``에 관한 새로운 티켓이 생성되었습니다 : <#{new_channel.id}>', view=None)
        await log_channel.send(log.new_ticket(user))


class SelectProblemView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SelectProblem())


class CloseBtn(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.stop()


class Ticket(commands.Cog, name="ticket"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="ticket",
        description="새로운 티켓을 생성합니다."
    )
    @checks.not_blacklisted()
    async def ticket(self, context: Context) -> None:
        await context.send(" ", view=SelectProblemView())

    @commands.hybrid_command(
        name="close",
        description="활성화된 티켓을 종료합니다."
    )
    @checks.not_blacklisted()
    async def close(self, context: Context) -> None:
        with open("database/ticket.json") as file:
            ticket_json = json.load(file)

        if context.channel.id in ticket_json["ticket_channel_ids"]:
            channel_id = context.channel.id

            button = CloseBtn()
            em = discord.Embed(
                title="BAMSAMBOT", description="정말 이 티켓을 종료하시겠습니까?", color=0xff9966)

            msg = await context.send(embed=em, view=button)
            await button.wait()

            index = ticket_json["ticket_channel_ids"].index(channel_id)
            del ticket_json["ticket_channel_ids"][index]

            with open('database/ticket.json', 'w') as f:
                json.dump(ticket_json, f, indent="\t", ensure_ascii=False)

            await context.channel.delete()

        else:
            em = discord.Embed(
                title="ERROR", description="`/close`는 활성화된 티켓 채팅방에서만 작동합니다.", color=0xff9966)
            await context.send(embed=em, view=None)


async def setup(bot):
    await bot.add_cog(Ticket(bot))
