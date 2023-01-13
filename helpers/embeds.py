import discord


class Color:
    def green():
        return 0x23C552

    def blue():
        return 0x00a8ff

    def blurple():
        return 0x9C84EF

    def yellow():
        return 0xffcc00

    def lightred():
        return 0xff9966

    def darkred():
        return 0xF84F31


def EmbedRed(title: str, content: str):
    embed = discord.Embed(
        title=title,
        description=content,
        color=Color.darkred()
    )
    return embed


def EmbedBlurple(title: str, content: str):
    embed = discord.Embed(
        title=title,
        description=content,
        color=Color.blurple()
    )
    return embed


def EmbedGreen(title: str, content: str):
    embed = discord.Embed(
        title=title,
        description=content,
        color=Color.green()
    )
    return embed


def EmbedYellow(title: str, content: str):
    embed = discord.Embed(
        title=title,
        description=content,
        color=Color("yellow")
    )
    return embed
