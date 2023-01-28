import discord


def EmbedRed(title: str, content: str):
    embed = discord.Embed(
        title=title,
        description=content,
        color=discord.Color.red()
    )
    return embed


def EmbedBlurple(title: str, content: str):
    embed = discord.Embed(
        title=title,
        description=content,
        color=discord.Color.blurple()
    )
    return embed


def EmbedGreen(title: str, content: str):
    embed = discord.Embed(
        title=title,
        description=content,
        color=discord.Color.green()
    )
    return embed


def EmbedYellow(title: str, content: str):
    embed = discord.Embed(
        title=title,
        description=content,
        color=discord.Color.yellow()
    )
    return embed
