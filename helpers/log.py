import discord
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime


async def LOG_CHANNEL():
    return int(1062130045340110978)


def new_ticket(userid):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `OPEN_TICKET`\nExecutor: <@{userid}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def warning_add(executorid, targetid, reason):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `WARN_ADD`\nExecutor: <@{executorid}>\nTarget: <@{targetid}>\nReason: <{reason}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def warning_remove(executorid, targetid):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `WARN_REMOVE`\nExecutor: <@{executorid}>\nTarget: <@{targetid}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def peridot_add(executorid, amount, targetid):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `PERIDOT_ADD`\nExecutor: <@{executorid}>\nAmount: `{amount}`\nTarget: <@{targetid}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def peridot_remove(executorid, amount, targetid):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `PERIDOT_REMOVE`\nExecutor: <@{executorid}>\nAmount: `{amount}`\nTarget: <@{targetid}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def token_add(executorid, amount, targetid):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `TOKEN_ADD`\nExecutor: <@{executorid}>\nAmount: `{amount}`\nTarget: <@{targetid}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def token_remove(executorid, amount, targetid):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `TOKEN_REMOVE`\nExecutor: <@{executorid}>\nAmount: `{amount}`\nTarget: <@{targetid}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def shop_buy(executorid, item):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `BUY_ITEM`\nExecutor: <@{executorid}>\nItem: `{item}`",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def purge(userid, amount, channelid):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `PURGE`\nExecutor: <@{userid}>\nAmount: `{amount}`\nChannel: <#{channelid}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def got_answer(userid):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `QUEST_ANSWER`\nUser: <@{userid}>\n",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def level_set(executorid, level, targetid):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `SET_LEVEL`\nExecutor: <@{executorid}>\nlevel: `{level}`\nTarget: <@{targetid}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def xp_set(executorid, level, targetid):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `SET_XP`\nExecutor: <@{executorid}>\nlevel: `{level}`\nTarget: <@{targetid}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def quote(executorid, msgauthorid, channel):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `QUOTE`\nExecutor: <@{executorid}>\nMessageAuthor: <@{msgauthorid}>\nChannel: <#{channel}>",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def redeem(userid, reward, code):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `REDEEM`\nExecutor: <@{userid}>\nReward: {reward}\nCode: `{code}`",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def give(executorid, targetid, type, amount):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `GIVE_ITEM`\nExecutor: <@{executorid}>\nTarget: <@{targetid}>\nItemType: {type.capitalize()}\nAmount: `{amount}`",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def item_add(executorid, targetid, itemname):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `ITEM_ADD`\nExecutor: <@{executorid}>\nTarget: <@{targetid}>\nItem: `{itemname}`",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed


def item_remove(executorid, targetid, itemname):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `ITEM_REMOVE`\nExecutor: <@{executorid}>\nTarget: <@{targetid}>\nItem: `{itemname}`",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed

def quest_temp(executorid, msg):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    embed = discord.Embed(
        title="Bamsambot Log",
        description=f"Type: `QUEST / PROTOCOL`\nExecutor: <@{executorid}>\nAnswer: `{msg}`",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=timecode)
    return embed