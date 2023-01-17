import discord
import requests
import textwrap
from discord.ext import commands
from discord.ext.commands import Context
from PIL import Image, ImageDraw, ImageFont

from helpers import checks


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="quote",
        description="메시지 답장에 사용하면 Quote 이미지를 만들어줍니다."
    )
    async def quote(self, context: Context) -> None:
        try:
            msg = context.message.reference
            id = msg.message_id
            message = await context.fetch_message(id)
            ico = message.author.avatar
            url = ico
            file_name = "icon.jpeg"
            await context.defer()

            response = requests.get(url)
            image = response.content

            with open("cogs/assets/Quote/" + file_name, "wb") as img:
                img.write(image)

            if message.content.replace("\n", "").isascii():
                para = textwrap.wrap(message.clean_content, width=26)
            else:
                para = textwrap.wrap(message.clean_content, width=13)

            icon = Image.open("cogs/assets/Quote/icon.jpeg")
            gradient = Image.open("cogs/assets/Quote/grad.jpeg")
            black = Image.open("cogs/assets/Quote/black.jpeg")

            w, h = (680, 370)
            w1, h1 = icon.size

            gradient = gradient.resize((w, h))
            black = black.resize((w, h))
            icon = icon.resize((h, h))

            # if cmd == "color":
            #     gradient = gradient.convert("L")
            #     new = Image.new(mode="RGBA", size=(w, h))
            #     icon = icon.convert("RGBA")
            #     black = black.convert("RGBA")
            # if not cmd:
            #     gradient = gradient.convert("L")
            #     new = Image.new(mode="L", size=(w, h))
            #     icon = icon.convert("L")
            #     black = black.convert("L")

            gradient = gradient.convert("L")
            new = Image.new(mode="L", size=(w, h))
            icon = icon.convert("L")
            black = black.convert("L")

            icon = icon.crop((40, 0, 680, 370))
            new.paste(icon)
            sa = Image.composite(new, black, gradient)
            draw = ImageDraw.Draw(sa)
            fnt = ImageFont.truetype(
                'cogs/assets/Fonts/NanumGothic-ExtraBold.ttf', 28)
            w2, h2 = draw.textsize("a", font=fnt)
            i = (int(len(para)/2)*w2)+len(para)*5
            current_h, pad = 120-i, 0

            for line in para:
                if message.content.replace("\n", "").isascii():
                    w3, h3 = draw.textsize(line.ljust(
                        int(len(line)/2+11), " "), font=fnt)
                    draw.text((11*(w - w3) / 13+10, current_h+h2),
                              line.ljust(int(len(line)/2+11), "　"), font=fnt, fill="#FFF")
                else:
                    w3, h3 = draw.textsize(line.ljust(
                        int(len(line)/2+5), "　"), font=fnt)
                    draw.text((11*(w - w3) / 13+10, current_h+h2),
                              line.ljust(int(len(line)/2+5), "　"), font=fnt, fill="#FFF")
                current_h += h3 + pad

            dr = ImageDraw.Draw(sa)
            font = ImageFont.truetype('cogs/assets/Fonts/NanumGothic.ttf', 15)

            try:
                membername = message.author.display_name.strip(
                    "༺ৡۣۜ͜ ৡ ""ৡۣۜ͜ ৡ༻ ")
            except:
                membername = message.author.display_name

            authorw, authorh = dr.textsize(
                f"- {str(membername)}", font=font)
            dr.text((480-int(authorw/2), current_h+h2+10),
                    f"    - {str(membername)}", font=font, fill="#FFF")

            sa.save("cogs/assets/Quote/result.png")
            file = discord.File("cogs/assets/Quote/result.png")

            await context.send(file=file)
            await context.message.delete()

        except Exception as e:
            await context.send(f"`/quote`는 메시지 답장에서만 작동합니다.\n`{e}`")


async def setup(bot):
    await bot.add_cog(Fun(bot))
