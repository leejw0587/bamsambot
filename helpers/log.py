import discord
import asyncio
from discord.ext import commands
from datetime import datetime

LOG_CHANNEL_ID = 1026400764408635402


async def new_ticket(author):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    msg = f"[INFO] {timecode} | New ticket opened by : {author}"

    return msg
