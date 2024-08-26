import discord
import json
import typing
import asyncio
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, db_manager, embeds


class JoinButton(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="한국인으로 입장",
        style=discord.ButtonStyle.green,
        custom_id="joinkr"
    )
    async def joinkr(self, interaction: discord.Interaction, button: discord.Button):
        Guest_Role = interaction.guild.get_role(1070680657166090330)
        Temp_Role = interaction.guild.get_role(1075031832409677914)
        user = interaction.user

        if Guest_Role not in interaction.user.roles:
            await interaction.user.add_roles(Guest_Role)
            await interaction.user.remove_roles(Temp_Role)
            await interaction.user.send(embed=embeds.EmbedGreen("입장", "뱀샘크루에 입장하였습니다!"))

            with open("database/userdata.json", encoding="utf-8") as file:
                userdata = json.load(file)
            if str(user.id) in userdata:
                pass
            else:
                newUser = {
                    str(user.id): {
                        "username": str(user),
                        "userid": str(user.id),
                        "peridot": 0,
                        "token": 0,
                        "xp": 0,
                        "level": 0,
                        "attendance": 0,
                        "last_attendance": ""
                    }
                }
                userdata.update(newUser)
                with open("database/userdata.json", 'w', encoding="utf-8") as file:
                    json.dump(userdata, file, indent="\t", ensure_ascii=False)

            with open("database/itemdata.json", encoding="utf-8") as file:
                itemdata = json.load(file)
            if str(user.id) in itemdata:
                pass
            else:
                newUser = {
                    str(user.id): {
                        "username": str(user),
                        "userid": str(user.id),
                        "inventory": [],
                        "voice_emoji_modify": False,
                        "voice_title_modify": False
                    }
                }
                itemdata.update(newUser)
                with open("database/itemdata.json", 'w', encoding="utf-8") as file:
                    json.dump(itemdata, file, indent="\t", ensure_ascii=False)

        else:
            await interaction.user.send(embed=embeds.EmbedRed("입장", "이미 입장한 계정입니다!"))

    @discord.ui.button(
        label="Join as Japanese",
        style=discord.ButtonStyle.green,
        custom_id="joinjp"
    )
    async def joinjp(self, interaction: discord.Interaction, button: discord.Button):
        Guest_Role = interaction.guild.get_role(1070680657166090330)
        Japanese_Role = interaction.guild.get_role(1070677016870928495)
        Temp_Role = interaction.guild.get_role(1075031832409677914)
        user = interaction.user

        if Guest_Role not in interaction.user.roles:
            await interaction.user.add_roles(Guest_Role)
            await interaction.user.add_roles(Japanese_Role)
            await interaction.user.remove_roles(Temp_Role)
            await interaction.user.send(embed=embeds.EmbedGreen("入場", "ベムセムクルーに入場しました！"))

            with open("database/userdata.json", encoding="utf-8") as file:
                userdata = json.load(file)
            if str(user.id) in userdata:
                pass
            else:
                newUser = {
                    str(user.id): {
                        "username": str(user),
                        "userid": str(user.id),
                        "peridot": 0,
                        "token": 0,
                        "xp": 0,
                        "level": 0,
                        "attendance": 0,
                        "last_attendance": ""
                    }
                }
                userdata.update(newUser)
                with open("database/userdata.json", 'w', encoding="utf-8") as file:
                    json.dump(userdata, file, indent="\t", ensure_ascii=False)

            with open("database/itemdata.json", encoding="utf-8") as file:
                itemdata = json.load(file)
            if str(user.id) in itemdata:
                pass
            else:
                newUser = {
                    str(user.id): {
                        "username": str(user),
                        "userid": str(user.id),
                        "inventory": [],
                        "voice_emoji_modify": False,
                        "voice_title_modify": False
                    }
                }
                itemdata.update(newUser)
                with open("database/itemdata.json", 'w', encoding="utf-8") as file:
                    json.dump(itemdata, file, indent="\t", ensure_ascii=False)

        else:
            await interaction.user.send(embed=embeds.EmbedRed("入場", "すでに入場しているアカウントです！"))

    @discord.ui.button(
        label="Join as Sub-ACC",
        style=discord.ButtonStyle.green,
        custom_id="joinsub"
    )
    async def joinsub(self, interaction: discord.Interaction, button: discord.Button):
        SubACC_Role = interaction.guild.get_role(
            1070676839074381904)  # 취급주의 역할
        Temp_Role = interaction.guild.get_role(1075031832409677914)
        user = interaction.user

        if SubACC_Role not in interaction.user.roles:
            await interaction.user.add_roles(SubACC_Role)
            await interaction.user.remove_roles(Temp_Role)
            await interaction.user.send(embed=embeds.EmbedGreen("Join", "You have joined Bamsam Crew!"))
        else:
            await interaction.user.send(embed=embeds.EmbedRed("Join", "You have already joined Bamsam Crew!"))


class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(JoinButton())

    @commands.hybrid_command(
        name="load",
        description="cog를 로드합니다. (개발자 전용)",
    )
    @app_commands.describe(cog="로드할 cog 이름")
    @checks.is_dev()
    async def load(self, context: Context, cog: str) -> None:
        """
        :param context: The hybrid command context.
        :param cog: The name of the cog to load.
        """
        try:
            await self.bot.load_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                title="Error!",
                description=f"Could not load the `{cog}` cog.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            title="Load",
            description=f"Successfully loaded the `{cog}` cog.",
            color=discord.Color.green()
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="unload",
        description="cog를 언로드합니다. (개발자 전용)",
    )
    @app_commands.describe(cog="언로드할 cog 이름")
    @checks.is_dev()
    async def unload(self, context: Context, cog: str) -> None:
        """
        :param context: The hybrid command context.
        :param cog: The name of the cog to unload.
        """
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                title="Error!",
                description=f"Could not unload the `{cog}` cog.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            title="Unload",
            description=f"Successfully unloaded the `{cog}` cog.",
            color=discord.Color.green()
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="reload",
        description="cog를 리로드합니다. (개발자 전용)",
    )
    @app_commands.describe(cog="리로드할 cog 이름")
    @checks.is_dev()
    async def reload(self, context: Context, cog: str) -> None:
        """
        :param context: The hybrid command context.
        :param cog: The name of the cog to reload.
        """
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
        except Exception:
            embed = discord.Embed(
                title="Error!",
                description=f"Could not reload the `{cog}` cog.",
                color=discord.Color.red()
            )
            await context.send(embed=embed)
            return
        embed = discord.Embed(
            title="Reload",
            description=f"Successfully reloaded the `{cog}` cog.",
            color=discord.Color.green()
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="say",
        description="입력한 메시지를 봇이 대신 말해줍니다. (창조자 전용)",
    )
    @app_commands.describe(message="보낼 메시지")
    @checks.is_owner()
    async def say(self, context: Context, *, message: str) -> None:
        """
        :param context: The hybrid command context.
        :param message: The message that should be repeated by the bot.
        """
        await context.defer(ephemeral=True)
        message = message.split("[br]")
        await context.channel.send("\n".join(message))

    @commands.hybrid_command(
        name="embed",
        description="봇이 embed 형태로 메시지를 보내줍니다. (창조자 전용)",
    )
    @app_commands.describe(message="보낼 메시지")
    @checks.is_owner()
    async def embed(self, context: Context, *, message: str, color: str = None) -> None:
        res = await context.send("Sending Embed ...")
        await res.delete()
        message = message.split("[br]")
        if color == None:
            color = discord.Color.blurple()
        else:
            color = int(color, 16)
        embed = discord.Embed(
            description="\n".join(message),
            color=color
        )
        await context.channel.send(embed=embed)

    @commands.hybrid_command(
        name="createjoin",
        description="입장 embed를 만드는 커맨드입니다. (개발자 전용)"
    )
    @checks.is_dev()
    async def createjoin(self, context: Context) -> None:
        await context.send("Wait a second...", delete_after=1)
        await context.channel.send(embed=embeds.EmbedBlurple(
            "입장 / 入場", "아래 버튼을 눌러 뱀샘크루에 입장하세요.\n下のボタンを押してべムセムクルーに入場してください。"), view=JoinButton())

    @commands.hybrid_command(
        name="newupdate",
        description="업데이트 알림 메시지를 보냅니다. (개발자 전용)"
    )
    @checks.is_dev()
    async def newupdate(self, context: Context):
        update_channel = context.guild.get_channel(1070686029377450105)
        config = self.bot.config
        notion_link = "https://bamsambot.notion.site/BamsamBot-Release-Notes"
        await update_channel.send(embed=embeds.EmbedBlurple("New Update!", f"뱀샘봇의 새로운 버전(`{config['version']}`)이 업데이트 되었습니다.\n업데이트 내용은 [여기]({notion_link})에서 확인하세요."))
        await context.send("MESSAGE SENT", delete_after=3)

    @commands.hybrid_command(
        name="createname",
        description="닉네임 embed를 만드는 커맨드입니다. (개발자 전용)"
    )
    @checks.is_dev()
    async def createname(self, context: Context):
        await context.send("Wait a second...", delete_after=1)

        embed = discord.Embed(
            title="Nickname",
            description="뱀샘크루에서 사용할 닉네임을 적어주세요. 닉네임은 아래와 같이 표시됩니다.\nべムセムクルーで使うニックネームを書いてください。 ニックネームは以下のように表示されます。\n\n**`༺ৡۣۜ͜ ৡ Nickname ৡۣۜ͜ ৡ༻`**",
            color=discord.Color.blurple()
        )
        await context.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 1075031666160046190:
            if message.author == self.bot.user or message.author.bot:
                return
            else:
                nickname = "༺ৡۣۜ͜ ৡ " + message.content + " ৡۣۜ͜ ৡ༻"
                await message.author.edit(nick=nickname)
                await message.delete()

                Temp_Role = message.guild.get_role(1075031832409677914)
                await message.author.add_roles(Temp_Role)

                await asyncio.sleep(1)
                embed = discord.Embed(
                    title="Nickname",
                    description=f"닉네임이 `{message.content}`으(로) 설정되었습니다. <#1071340194244087819>로 이동하여 인증을 진행해주세요.\nニックネームが`{message.content}`に設定されました。 <#1071340194244087819>に移動して認証を進めてください。"
                )
                await message.channel.send(content=message.author.mention, embed=embed, delete_after=5)

        else:
            return


async def setup(bot):
    await bot.add_cog(Owner(bot))
