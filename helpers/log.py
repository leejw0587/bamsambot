import discord
from discord.ext import commands
from datetime import datetime


def new_ticket(user):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    msg = f"[INFO] {timecode} | New ticket opened by : <@{user.id}>"
    return msg


def warning(type, context, user):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    msg = f"[INFO] {timecode} | <@{context.author.id}> {type}ed Warning to <@{user.id}>"
    return msg


def peridot(type, context, user, amount):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    msg = f"[INFO] {timecode} | <@{context.author.id}> {type}ed {amount} Peridot to <@{user.id}>"
    return msg


def token(type, context, user, amount):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    msg = f"[INFO] {timecode} | <@{context.author.id}> {type}ed {amount} Token to <@{user.id}>"
    return msg


def shop_buy(context, item):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    msg = f"[SHOP] {timecode} | <@{context.author.id}> bought {item}"
    return msg


def purge(context, amount):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    msg = f"[INFO] {timecode} | <@{context.author.id}> purged `{amount}` message(s) in <#{context.channel.id}>"
    return msg


def got_answer(user):
    now = datetime.now()
    timecode = now.strftime('%Y-%m-%d %H:%M:%S')
    msg = f"[QUEST] {timecode} | <@{user.id}> got answer!"
    return msg
