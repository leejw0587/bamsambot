import discord
import requests
import textwrap
import random
import json
from discord.ext import commands
from discord.ext.commands import Context
from PIL import Image, ImageDraw, ImageFont

from helpers import checks, embeds

PERIDOT_EMOJI = "<:peridot:722474684045721973>"
RATIO = 1.1


class CoinFlipChoice(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="앞면", style=discord.ButtonStyle.blurple)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "앞면"
        self.stop()

    @discord.ui.button(label="뒷면", style=discord.ButtonStyle.blurple)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "뒷면"
        self.stop()


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

            await context.message.delete()
            await context.send(file=file)

        except Exception as e:
            await context.send(f"`/quote`는 메시지 답장에서만 작동합니다.\n`{e}`")

    @commands.hybrid_command(
        name="coinflip",
        description="동전 던지기 미니게임을 합니다."
    )
    @checks.is_owner()
    async def coinflip(self, context: Context, bet: int = 0) -> None:
        with open("database/userdata.json", encoding="utf-8") as file:
            userdata = json.load(file)

        if bet == 0:
            pass
        else:
            if userdata[str(context.author.id)]["peridot"] >= bet:
                pass
            else:
                await context.send(embed=embeds.EmbedRed("Error!", "페리도트가 부족합니다."))
                return

        userdata[str(context.author.id)]["peridot"] = userdata[str(
            context.author.id)]["peridot"] - bet

        bet_str = format(bet, ',d')
        buttons = CoinFlipChoice()
        embed = discord.Embed(
            title="동전 던지기",
            description=f"동전의 방향을 골라주세요.\n베팅: {bet_str} {PERIDOT_EMOJI}\n배당: `{RATIO}`배",
            color=0x9C84EF
        )
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()
        result = random.choice(["앞면", "뒷면"])
        if buttons.value == result:
            reward = int(bet * RATIO)
            reward_str = format(reward, ',d')
            userdata[str(context.author.id)]["peridot"] = userdata[str(
                context.author.id)]["peridot"] + reward
            embed = discord.Embed(
                title="맞았습니다!",
                description=f"당신의 선택은 `{buttons.value}` 이고, 던진 결과는 `{result}` 입니다.\n{reward_str} {PERIDOT_EMOJI}를 얻었습니다.",
                color=0x9C84EF
            )
        else:
            embed = discord.Embed(
                title="틀렸습니다!",
                description=f"당신의 선택은 `{buttons.value}` 이고, 던진 결과는 `{result}` 입니다.\n{bet_str} {PERIDOT_EMOJI}를 잃었습니다.",
                color=0xE02B2B
            )
        await message.edit(embed=embed, view=None, content=None)

        with open("database/userdata.json", 'w', encoding="utf-8") as file:
            json.dump(userdata, file, indent="\t", ensure_ascii=False)


async def setup(bot):
    await bot.add_cog(Fun(bot))
