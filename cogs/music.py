import asyncio
import discord
import typing
import wavelink
import datetime

from wavelink import TrackSource
from typing import cast
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import embeds


class Music(commands.Cog, name="music"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print("Connecting to Lavalink node...")
        nodes = [wavelink.Node(uri="http://127.0.0.1:2333", password="youshallnotpass")]
        await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=None)
        

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        print(f"Wavelink Node connected: {payload.node!r} | Resumed: {payload.resumed}")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        
        if not player:
            return

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track

        embed = discord.Embed(
            title=f":notes: {track.title}", color=embeds.discord.Color.blurple())
        embed.add_field(name="곡 길이", value=str(
            datetime.timedelta(milliseconds=int(track.length))), inline=True)
        embed.add_field(
            name="링크", value=f"[클릭]({track.uri})", inline=True)
        

        if track.artwork:
            embed.set_thumbnail(url=track.artwork)

        if original and original.recommended:
            embed.description = f"\n\n(자동재생에 의해 추가된 노래임)"

        await player.home.send(embed=embed)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            return

        if player.autoplay != wavelink.AutoPlayMode.disabled:
            return
        else:
            try:
                await player.play(player.queue.get(), volume=30)
            except:
                pass

    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, player: wavelink.player) -> None:
        await player.home.send(embed=embeds.EmbedBlurple("Music", f"`{player.inactive_timeout}`초간 활동이 없어 음성 채널과 연결을 해제합니다."))
        player.autoplay = wavelink.AutoPlayMode.disabled
        await player.disconnect()

    @commands.hybrid_command(
        name="join",
        description="음성 채널에 연결합니다."
    )
    async def join(self, context: Context, channel: typing.Optional[discord.VoiceChannel]):
        player: wavelink.Player = cast(wavelink.Player, context.voice_client)
        if channel is None:
            channel = context.author.voice.channel

        if not player:
            try:
                player = await channel.connect(cls=wavelink.Player)  # type: ignore
                await context.send(embed=embeds.EmbedBlurple("Music", f"`{channel.name}`에 연결하였습니다."))
            except Exception as e:
                return await context.send(embed=embeds.EmbedRed("Music", "음성 채널에 연결할 수 없습니다."))


    @commands.hybrid_command(
        name="leave",
        description="연결된 음성 채널에서 나갑니다."
    )
    async def leave(self, context: Context):
        player: wavelink.Player = cast(wavelink.Player, context.voice_client)
        if not player:
            return await context.send(embed=embeds.EmbedRed("Music", "연결된 음성 채널이 없습니다."))

        await player.disconnect()
        await context.send(embed=embeds.EmbedBlurple("Music", f"음성 채널과 연결이 해제되었습니다."))


    @commands.hybrid_command(
        name="p",
        description="음악을 재생합니다."
    )
    @app_commands.describe(query="검색어 또는 링크")
    async def play(self, context: Context, *, query: str):
        player: wavelink.Player
        player = cast(wavelink.Player, context.voice_client)

        if not player:
            try:
                player = await context.author.voice.channel.connect(cls=wavelink.Player)  # type: ignore
            except AttributeError:
                return await context.send(embed=embeds.EmbedRed("Music", "연결된 음성 채널이 없습니다."))
            except discord.ClientException:
                return await context.send(embed=embeds.EmbedRed("Music", "해당 음성 채널에 접속할 수 없습니다."))
                
            
        if not hasattr(player, "home"):
            player.home = context.channel
        elif player.home != context.channel:
            return await context.send(embed=embeds.EmbedRed("Music", f"{player.home.mention}에서만 노래를 재생할 수 있습니다."))
        
        tracks: wavelink.Search = await wavelink.Playable.search(query, source=TrackSource.YouTube)
        if not tracks:
            return await context.send(embed=embeds.EmbedRed("Music", "노래를 찾을 수 없습니다."))
            
        player.autoplay = wavelink.AutoPlayMode.disabled
        player.inactive_timeout = 60

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await context.send(embed=embeds.EmbedBlurple("Music", f"플레이리스트 **`{tracks.name}`** ({added} 곡)을(를) 재생목록에 추가하였습니다."))
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            await context.send(embed=embeds.EmbedBlurple("Music", f"**`{track}`**을(를) 재생목록에 추가하였습니다."))

        if not player.playing:
            await player.play(player.queue.get(), volume=30)



    @commands.hybrid_command(
        name="pause",
        description="재생중인 음악을 일시중지/재개 합니다.",
    )
    async def pause(self, context: Context):
        player: wavelink.Player = cast(wavelink.Player, context.voice_client)
        if not player:
            return await context.send(embed=embeds.EmbedRed("Music", "재생중인 노래가 없습니다."))

        if not player.paused:
            await context.send(embed=embeds.EmbedBlurple("Music", f"노래를 일시정지합니다."))
        else:
            await context.send(embed=embeds.EmbedBlurple("Music", f"노래 재생을 재개합니다."))
        await player.pause(not player.paused)


    @commands.hybrid_command(
        name="skip",
        description="재생중인 노래를 건너뜁니다."
    )
    async def skip(self, context: Context):
        player: wavelink.Player = cast(wavelink.Player, context.voice_client)
        if not player:
            return await context.send(embed=embeds.EmbedRed("Music", "재생중인 노래가 없습니다."))

        await context.send(embed=embeds.EmbedBlurple("Music", f"`{player.current.title}`을(를) 건너뜁니다."))
        await player.skip(force=True)
        
        try:
            await player.play(player.queue.get(), volume=30)
        except:
            pass

        
    @commands.hybrid_command(
        name="nowplaying",
        description="현재 재생중인 음악을 보여줍니다.",
        aliases=["np"]
        )
    async def nowplaying(self, context: Context):
        player: wavelink.Player = cast(wavelink.Player, context.voice_client)
        if not player:
            return await context.send(embed=embeds.EmbedRed("Music", "현재 재생중인 노래가 없습니다."))

        if player.playing:
            track = player.current

            embed = discord.Embed(
            title=f":notes: {track.title}", color=embeds.discord.Color.blurple())
            embed.add_field(name="곡 길이", value=str(
                datetime.timedelta(milliseconds=int(track.length))), inline=True)
            embed.add_field(
                name="링크", value=f"[클릭]({track.uri})", inline=True)
            embed.set_thumbnail(url=track.artwork)

            return await context.send(embed=embed)

    

    @commands.hybrid_command(
        name="queue",
        description="재생 목록을 보여줍니다."
    )
    async def queue(self, context: Context):
        player: wavelink.Player = cast(wavelink.Player, context.voice_client)
        
        if not player:
            return await context.send(embed=embeds.EmbedRed("Music", "현재 재생중인 노래가 없습니다."))
        else:
            queue = player.queue
        
        if queue.is_empty == False:
            playtime = 0
            for i, track in enumerate(queue):
                playtime += track.length
            
            playtime = datetime.timedelta(milliseconds=playtime)

            embed = discord.Embed(
                title=f":notes: 재생목록 ({playtime}): ",
                description="\n".join(f"**{i+1}. {track}**" for i, track in enumerate(queue)),
                color=discord.Color.blurple()
            )
            return await context.send(embed=embed)
        
        else:
            return await context.send(embed=embeds.EmbedYellow("Music", "재생목록이 비어있습니다."))


    @commands.hybrid_command(
        name='remove',
        description='재생 목록에서 특정 노래를 제거합니다.'
    )
    @app_commands.describe(number="제거할 노래의 번호")
    async def remove(self, context: Context, number: int):
        player: wavelink.Player = cast(wavelink.Player, context.voice_client)
        queue = player.queue

        if number <= 0:
            return await context.reply(embed=embeds.EmbedRed("Music", "1 이상의 정수만 입력 가능합니다."))
        else:
            try:
                removed_track = queue[number-1]
                queue.delete(number-1)
                return await context.send(embed=embeds.EmbedBlurple("Music", f"`{removed_track.title}`을 재생목록에서 제거하였습니다."))
            except:
                return await context.send(embed=embeds.EmbedRed("Music", "제거 도중 문제가 발생하였습니다."))

    @commands.hybrid_command(
        name="autoplay",
        description="자동재생 기능을 설정합니다."
    )
    async def autoplay(self, context: Context):
        player: wavelink.Player = cast(wavelink.Player, context.voice_client)

        if not player:
            return await context.send(embed=embeds.EmbedRed("Music", "현재 재생중인 노래가 없습니다."))

        if player.autoplay == wavelink.AutoPlayMode.enabled:
            player.autoplay = wavelink.AutoPlayMode.disabled
            return await context.send(embed=embeds.EmbedBlurple("Music", f"자동재생 기능을 비활성화하였습니다."))
        else:
            player.autoplay = wavelink.AutoPlayMode.enabled
            return await context.send(embed=embeds.EmbedBlurple("Music", f"자동재생 기능을 활성화하였습니다.\n이 기능은 새로운 노래를 추가하면 비활성화됩니다."))

    

    @commands.hybrid_command(
        name='loop',
        description='[WIP] 반복재생 여부를 설정합니다.'
    )
    async def loop(self, context: Context):
        return await context.send(embed=embeds.EmbedYellow("Music", "현재 개발중인 기능입니다."))
    

    @commands.hybrid_command(
        name="shuffle",
        description="[WIP] 재생목록을 무작위로 재배열합니다."
    )
    async def shuffle(self, context: Context):
        return await context.send(embed=embeds.EmbedYellow("Music", "현재 개발중인 기능입니다."))
    
    @commands.hybrid_command(
        name="swap",
        description="[WIP] 두 노래의 재생 순서를 바꿉니다."
    )
    @app_commands.describe(first="바꿀 노래의 번호", second="바꿀 노래의 번호")
    async def swap(self, context: Context, first: int, second: int):
        return await context.send(embed=embeds.EmbedYellow("Music", "현재 개발중인 기능입니다."))

    @commands.hybrid_command(
        name="empty",
        description="[WIP] 재생목록을 초기화합니다."
    )
    async def empty(self, context: Context):
        return await context.send(embed=embeds.EmbedYellow("Music", "현재 개발중인 기능입니다."))
    
async def setup(bot):
    await bot.add_cog(Music(bot))
