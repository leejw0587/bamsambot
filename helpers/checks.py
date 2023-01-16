import json
import discord
from typing import Callable, TypeVar

from discord.ext import commands

from exceptions import *
from helpers import db_manager

T = TypeVar("T")


def is_owner() -> Callable[[T], T]:
    async def predicate(context: commands.Context) -> bool:
        with open("config.json") as file:
            data = json.load(file)
        if context.author.id not in data["owners"]:
            raise UserNotOwner
        return True

    return commands.check(predicate)


def is_informant() -> Callable[[T], T]:
    async def predicate(context: commands.Context) -> bool:
        with open("config.json") as file:
            data = json.load(file)
        if context.author.id not in data["informants"]:
            raise UserNotInformant
        return True

    return commands.check(predicate)


def not_blacklisted() -> Callable[[T], T]:
    async def predicate(context: commands.Context) -> bool:
        if await db_manager.is_blacklisted(context.author.id):
            raise UserBlacklisted
        return True

    return commands.check(predicate)


def has_check_role() -> Callable[[T], T]:
    async def predicate(context: commands.Context) -> bool:
        CHECK = discord.utils.get(context.guild.roles, id=390821573315002369)

        if CHECK not in context.author.roles:
            raise UserNotHasCheck
        return True

    return commands.check(predicate)
