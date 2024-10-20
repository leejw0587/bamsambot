import asyncio
import json
import os
import platform
import random
import sys

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from datetime import datetime
from dotenv import load_dotenv

import exceptions

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

"""	
bot intents:
https://discordpy.readthedocs.io/en/latest/intents.html
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents


Default Intents:
intents.bans = True
intents.dm_messages = True
intents.dm_reactions = True
intents.dm_typing = True
intents.emojis = True
intents.emojis_and_stickers = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guild_scheduled_events = True
intents.guild_typing = True
intents.guilds = True
intents.integrations = True
intents.invites = True
intents.messages = True # `message_content` is required to get the content of the messages
intents.reactions = True
intents.typing = True
intents.voice_states = True
intents.webhooks = True

Privileged Intents:
intents.members = True
intents.message_content = True
intents.presences = True
"""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


bot = Bot(command_prefix=config["prefix"], intents=intents, help_command=None)


async def init_db():
    async with aiosqlite.connect("database/database.db") as db:
        with open("database/schema.sql") as file:
            await db.executescript(file.read())
        await db.commit()


"""
- bot.config # In here
- self.bot.config # In cogs
"""
bot.config = config


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user.name}")
    print(f"discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()
    if config["sync_commands_globally"]:
        print("Syncing commands globally...")
        await bot.tree.sync()


@tasks.loop(minutes=1.0)
async def status_task() -> None:
    statuses = ["/help"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    :param message: The message that was sent.
    """
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    welcome_channel = bot.get_channel(1070686070011871272)

    embed = discord.Embed(
        title="WELCOME", description=f"{member.mention}님, 뱀샘크루에 오신 것을 환영합니다!", color=0x9C84EF)
    await welcome_channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    welcome_channel = bot.get_channel(1070686070011871272)

    embed = discord.Embed(
        title="GOOD BYE", description=f"`{member.name}`님이 뱀샘크루를 떠났습니다.", color=0x9C84EF)
    await welcome_channel.send(embed=embed)


@bot.event
async def on_command_completion(context: Context) -> None:
    """
    :param context: The context of the command that has been executed.
    """
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])

    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')

    if context.guild is not None:
        print(
            f"[INFO] {timecode} | Executed {executed_command} command by {context.author}")
    else:
        print(
            f"[INFO] {timecode} | Executed {executed_command} command by {context.author} in DMs")


@bot.event
async def on_command_error(context: Context, error) -> None:
    """
    :param context: The context of the normal command that failed executing.
    :param error: The error that has been faced.
    """
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            title="진정하세요!",
            description=f"{f'{round(hours)} 시간' if round(hours) > 0 else ''} {f'{round(minutes)} 분' if round(minutes) > 0 else ''} {f'{round(seconds)} 초' if round(seconds) > 0 else ''} 뒤에 이 커맨드를 다시 사용할 수 있습니다.",
            color=discord.Color.yellow()
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserBlacklisted):
        embed = discord.Embed(
            title="Error!",
            description="당신은 블랙리스트에 포함되어 있습니다.",
            color=discord.Color.red()
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserNotOwner):

        embed = discord.Embed(
            title="Error!",
            description="창조자만 이 명령어를 사용할 수 있습니다.",
            color=discord.Color.red()
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="당신은 이 명령어를 사용할 권한이 없습니다. `" + ", ".join(
                error.missing_permissions) + "`",
            color=discord.Color.red()
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingRole):
        embed = discord.Embed(
            title="Error!",
            description=f"당신은 이 명령어를 사용하기 위한 역할이 없습니다. <@&{error.missing_role}>",
            color=discord.Color.red()
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="Bot missing permission: `" + ", ".join(
                error.missing_permissions) + "`",
            color=discord.Color.red()
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="Error!",
            description="알 수 없는 커맨드입니다.",
            color=discord.Color.red()
        )
        await context.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Error!",
            description=f"커맨드를 실행하던 중 오류가 발생했습니다.\n`{error}`",
            color=discord.Color.red()
        )
        await context.send(embed=embed)
    raise error


async def load_cogs() -> None:
    for file in os.listdir(f"./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


asyncio.run(init_db())
asyncio.run(load_cogs())

load_dotenv()
TOKEN = os.environ.get('main_token')
bot.run(TOKEN)
