import asyncio
import discord
import typing
import wavelink
import datetime

from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import embeds


class Music(commands.Cog, name="music"):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.position = 0
        self.repeat = False
        self.repeatMode = "NONE"
        self.playingTextChannel = 0

    @commands.Cog.listener()
    async def on_ready(self):
        await wavelink.NodePool.create_node(bot=self.bot, host="127.0.0.1", port="2333", password="youshallnotpass", region="asia")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.id == self.bot.user.id:
            return

        elif before.channel is None:
            node = wavelink.NodePool.get_node()
            player = node.get_player(after.channel.guild)

            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 10:
                    await voice.disconnect()
                    self.queue.clear()
                    await player.stop()
                if not voice.is_connected():
                    break

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node <{node.identifier}> is now Ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.Track):
        try:
            self.queue.pop(0)
        except:
            pass

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        if str(reason) == "FINISHED":
            if not len(self.queue) == 0:
                next_track: wavelink.Track = self.queue[0]
                channel = self.bot.get_channel(self.playingTextChannel)

                try:
                    await player.play(next_track)
                except:
                    return await channel.send(embed=embeds.EmbedRed("BamsamMusic", "재생 도중 문제가 발생하였습니다."))
                embed = discord.Embed(
                    title=f":notes: {next_track.title}", color=embeds.Color.blurple())
                embed.set_thumbnail(url=next_track.thumbnail)
                embed.add_field(name="곡 길이", value=str(
                    datetime.timedelta(seconds=int(next_track.length))), inline=True)
                embed.add_field(
                    name="링크", value=f"[클릭]({next_track.uri})", inline=True)
                await channel.send(embed=embed)
            else:
                pass
        else:
            print(reason)

    @commands.hybrid_command(
        name="join",
        description="음성 채널에 연결합니다."
    )
    async def join(self, context: Context, channel: typing.Optional[discord.VoiceChannel]):
        if channel is None:
            channel = context.author.voice.channel

        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        if player is not None:
            if player.is_connected():
                return await context.send(embed=embeds.EmbedRed("BamsamMusic", "이미 음성 채널에 연결되어 있습니다."))

        await channel.connect(cls=wavelink.Player)
        await context.send(embed=embeds.EmbedBlurple("BamsamMusic", f"`{channel.name}`에 연결하였습니다."))

    @commands.hybrid_command(
        name="leave",
        description="연결된 음성 채널에서 나갑니다."
    )
    async def leave(self, context: Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        if player is None:
            return await context.send(embed=embeds.EmbedRed("BamsamMusic", "연결된 음성 채널이 없습니다."))

        await player.disconnect()

        await context.send(embed=embeds.EmbedBlurple("BamsamMusic", f"음성 채널과 연결이 해제되었습니다."))

    @commands.hybrid_command(
        name="play",
        description="음악을 재생합니다."
    )
    @app_commands.describe(query="검색어 또는 유튜브 링크")
    async def play(self, context: Context, *, query: str):
        try:
            search = await wavelink.YouTubeTrack.search(query=query, return_first=True)
        except:
            return await context.reply(embed=embeds.EmbedRed("BamsamMusic", "검색 도중 문제가 발생하였습니다."))

        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        if not context.voice_client:
            vc: wavelink.Player = await context.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = context.voice_client

        if not vc.is_playing():
            try:
                await vc.play(search)
            except:
                return await context.reply(embed=embeds.EmbedRed("BamsamMusic", "재생 도중 문제가 발생하였습니다."))
        else:
            self.queue.append(search)

        embed = discord.Embed(
            title=f":notes: {search}", color=embeds.Color.blurple())
        embed.set_thumbnail(url=search.thumbnail)
        embed.add_field(name="곡 길이", value=str(
            datetime.timedelta(seconds=int(search.length))), inline=True)
        embed.add_field(
            name="링크", value=f"[클릭]({search.uri})", inline=True)
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="stop",
        description="재생중인 음악을 중지합니다."
    )
    async def stop(self, context: Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        if player is None:
            return await context.send(embed=embeds.EmbedRed("BamsamMusic", "연결된 음성 채널이 없습니다."))

        self.queue.clear()

        if player.is_playing():
            await player.stop()
            return await context.send(embed=embeds.EmbedBlurple("BamsamMusic", f"재생을 중지하였습니다."))
        else:
            return await context.send(embed=embeds.EmbedRed("BamsamMusic", "재생중인 노래가 없습니다."))

    @commands.hybrid_command(
        name="pause",
        description="재생중인 음악을 일시중지합니다."
    )
    async def pause(self, context: Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        if player is None:
            return await context.send(embed=embeds.EmbedRed("BamsamMusic", "연결된 음성 채널이 없습니다."))

        if not player.is_paused():
            if player.is_playing():
                await player.pause()
                return await context.send(embed=embeds.EmbedBlurple("BamsamMusic", f"재생을 일시중지하였습니다."))
            else:
                return await context.send(embed=embeds.EmbedRed("BamsamMusic", "재생중인 노래가 없습니다."))
        else:
            return await context.send(embed=embeds.EmbedRed("BamsamMusic", "이미 일시중지 상태입니다."))

    @commands.hybrid_command(
        name="resume",
        description="일시중지한 음악을 재개합니다."
    )
    async def resume(self, context: Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        if player is None:
            return await context.send(embed=embeds.EmbedRed("BamsamMusic", "연결된 음성 채널이 없습니다."))

        if player.is_paused():
            await player.resume()
            return await context.send(embed=embeds.EmbedBlurple("BamsamMusic", f"재생을 다시 시작합니다."))
        else:
            if not len(self.queue) == 0:
                track: wavelink.Track = self.queue[0]
                player.play(track)
                embed = discord.Embed(
                    title=f":notes: {track}", color=embeds.Color.blurple())
                embed.set_thumbnail(url=track.thumbnail)
                embed.add_field(name="곡 길이", value=str(
                    datetime.timedelta(seconds=int(track.length))), inline=True)
                embed.add_field(
                    name="링크", value=f"[클릭]({track.uri})", inline=True)
                return await context.reply(embed=embed)
            else:
                return await context.send(embed=embeds.EmbedRed("BamsamMusic", "일시중지 상태가 아닙니다."))

    @commands.hybrid_command(
        name="volume",
        description="볼륨을 설정합니다."
    )
    @app_commands.describe(volume="설정할 볼륨")
    async def volume(self, context: Context, volume: int):
        if volume > 100:
            return await context.send(embed=embeds.EmbedRed("BamsamMusic", "볼륨은 0과 100사이의 정수로만 설정 가능합니다."))
        elif volume < 1:
            return await context.send(embed=embeds.EmbedRed("BamsamMusic", "볼륨은 0과 100사이의 정수로만 설정 가능합니다."))

        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        await player.set_volume(volume)
        await context.send(embed=embeds.EmbedBlurple("BamsamMusic", f"볼륨을 {volume}(으)로 설정하였습니다."))

    # @commands.hybrid_command(name="playnow", aliases=["pn"])
    # async def play_now_command(self, context: Context, *, search: str):
    #     try:
    #         search = await wavelink.YouTubeTrack.search(query=search, return_first=True)
    #     except:
    #         return await context.reply(embed=discord.Embed(title="Something went wrong while searching for this track", color=discord.Color.from_rgb(255, 255, 255)))

    #     node = wavelink.NodePool.get_node()
    #     player = node.get_player(context.guild)

    #     if not context.voice_client:
    #         vc: wavelink.Player = await context.author.voice.channel(cls=wavelink.Player)
    #         await player.connect(context.author.voice.channel)
    #     else:
    #         vc: wavelink.Player = context.voice_client

    #     try:
    #         await vc.play(search)
    #     except:
    #         return await context.reply(embed=discord.Embed(title="Something went wrong while playing this track", color=discord.Color.from_rgb(255, 255, 255)))
    #     await context.reply(embed=discord.Embed(title=f"Playing: **{search.title}** Now", color=discord.Color.from_rgb(255, 255, 255)))

    @commands.hybrid_command(
        name="nowplaying",
        description="현재 재생중인 음악을 보여줍니다."
    )
    async def now_playing(self, context: Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        if player is None:
            return await context.reply(embed=embeds.EmbedRed("BamsamMusic", "연결된 음성 채널이 없습니다."))

        if player.is_playing():
            mbed = discord.Embed(
                title=f"Now Playing: {player.track}",
                # you can add url as one the arugument over here, if you want the user to be able to open the video in youtube
                # url = f"{player.track.info['uri']}"
                color=discord.Color.from_rgb(255, 255, 255)
            )

            embed = discord.Embed(
                title=f":notes: {player.track}", color=embeds.Color.blurple())
            embed.set_thumbnail(url=player.track.thumbnail)
            embed.add_field(name="곡 길이", value=str(
                datetime.timedelta(seconds=int(player.track.length))), inline=True)
            embed.add_field(
                name="링크", value=f"[클릭]({player.track.uri})", inline=True)
            return await context.reply(embed=embed)

        else:
            await context.reply(embed=embeds.EmbedRed("BamsamMusic", "재생중인 노래가 없습니다."))

    @commands.hybrid_command(
        name="search",
        description="노래 검색 결과를 직접 선택하여 재생합니다."

    )
    async def search(self, context: Context, *, query: str):
        try:
            tracks = await wavelink.YouTubeTrack.search(query=query)
        except:
            return await context.reply(embed=embeds.EmbedRed("BamsamMusic", "검색 도중 문제가 발생하였습니다."))

        if tracks is None:
            return await context.reply(embed=embeds.EmbedBlurple("BamsamMusic", "검색 결과를 찾지 못했습니다."))

        embed = discord.Embed(
            title="노래를 골라주세요: ",
            description=(
                "\n".join(f"**{i+1}. {t.title}**" for i, t in enumerate(tracks[:5]))),
            color=embeds.Color.blurple()
        )
        msg = await context.reply(embed=embed)

        emojis_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '❌']
        emojis_dict = {
            '1️⃣': 0,
            "2️⃣": 1,
            "3️⃣": 2,
            "4️⃣": 3,
            "5️⃣": 4,
            "❌": -1
        }

        for emoji in list(emojis_list[:min(len(tracks), len(emojis_list))]):
            await msg.add_reaction(emoji)

        def check(res, user):
            return (res.emoji in emojis_list and user == context.author and res.message.id == msg.id)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            return
        else:
            await msg.delete()

        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        try:
            if emojis_dict[reaction.emoji] == -1:
                return
            choosed_track = tracks[emojis_dict[reaction.emoji]]
        except:
            return

        vc: wavelink.Player = context.voice_client or await context.author.voice.channel.connect(cls=wavelink.Player)

        if not player.is_playing() and not player.is_paused():
            try:
                await vc.play(choosed_track)
            except:
                return await context.reply(embed=discord.Embed(embed=embeds.EmbedRed("BamsamMusic", "재생 중 문제가 발생하였습니다.")))
        else:
            self.queue.append(choosed_track)

        await context.reply(embed=embeds.EmbedBlurple("BamsamMusic", f"`{choosed_track.title}`을(를) 재생목록에 추가하였습니다."))

    @commands.hybrid_command(
        name="skip",
        description="재생중인 노래를 건너뜁니다."
    )
    async def skip_command(self, context: Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        if not len(self.queue) == 0:
            next_track: wavelink.Track = self.queue[0]
            try:
                await player.play(next_track)
            except:
                return await context.reply(embed=discord.Embed(embed=embeds.EmbedRed("BamsamMusic", "재생 중 문제가 발생하였습니다.")))

            embed = discord.Embed(
                title=f":notes: {next_track.title}", color=embeds.Color.blurple())
            embed.set_thumbnail(url=next_track.thumbnail)
            embed.add_field(name="곡 길이", value=str(
                datetime.timedelta(seconds=int(next_track.length))), inline=True)
            embed.add_field(
                name="링크", value=f"[클릭]({next_track.uri})", inline=True)
            await context.reply(embed=embed)
        else:
            await context.reply(embed=discord.Embed(embed=embeds.EmbedRed("BamsamMusic", "재생목록이 비어있습니다.")))

    # this command would queue a song if some args(search) is provided else it would just show the queue
    @commands.hybrid_command(
        name="queue",
        description="재생 목록을 보여줍니다."
    )
    async def queue_command(self, context: Context, *, search=None):
        node = wavelink.NodePool.get_node()
        player = node.get_player(context.guild)

        if search is None:
            if not len(self.queue) == 0:
                embed = discord.Embed(
                    title=f":notes: {player.track}" if player.is_playing else "재생목록: ",
                    description="\n".join(f"**{i+1}. {track}**" for i, track in enumerate(self.queue[:10])) if not player.is_playing else "**재생목록: **\n"+"\n".join(
                        f"**{i+1}. {track}**" for i, track in enumerate(self.queue[:10])),
                    color=embeds.Color.blurple()
                )
                return await context.reply(embed=embed)
            else:
                return await context.reply(embed=embeds.EmbedRed("BamsamMusic", "재생목록이 비어있습니다."))
        else:
            try:
                track = await wavelink.YoutubeTrack.search(query=search, return_first=True)
            except:
                return await context.reply(embed=embeds.EmbedRed("BamsamMusic", "검색 중 문제가 발생하였습니다."))

            if not context.voice_client:
                vc: wavelink.Player = await context.author.voice.channel(cls=wavelink.Player)
                await player.connect(context.author.voice.channel)
            else:
                vc: wavelink.Player = context.voice_client

            if not vc.isp_playing():
                try:
                    await vc.play(track)
                except:
                    return await context.reply(embed=embeds.EmbedRed("BamsamMusic", "재생 중 문제가 발생하였습니다."))
            else:
                self.queue.append(track)

            await context.reply(embed=embeds.EmbedBlurple("BamsamMusic", f"{track.title}을(를) 재생목록에 추가하였습니다."))


async def setup(bot):
    await bot.add_cog(Music(bot))
