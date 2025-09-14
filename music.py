import discord
from discord.ext import commands

import asyncio

from responses import get_response
from ytdl import YTDLSource

from collections import deque

class Music(commands.Cog):
    """Defines a group of related music commands aka a Cog"""
    def __init__(self, bot):
        self.bot = bot
        self.queue = deque()
        self.current = None

    async def play_next(self, ctx):
        if self.queue:
            self.current = self.queue.popleft()
            ctx.voice_client.play(
                self.current,
                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
            )
            await ctx.send(get_response("now_playing", title=self.current.title))
        else:
            self.current = None
            await ctx.send(get_response("queue_empty"))
    
    # move to most recently requested voice channel if currently engaged, otherwise connect to voice
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Join voice channel"""
        if ctx.voice_Client is not None:
            return await ctx.voice_client.move_to(channel)
        
        await channel.connect()
    
    # plays audio file (defined by query)
    @commands.command()
    async def play(self, ctx, *, query):
        """play local file in voice"""
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
            
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

        # add bot personality here
        await ctx.send(get_response("now_playing", title=query))

    # takes youtube url, routes it through YTDLSource stream=False and play()
    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays audio from youtube (pre-download)"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=False)
            self.queue.append(player)
            await ctx.send(get_response("add_queue", len=1))

            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)

    @commands.command()
    async def stream(self, ctx, *, url):
        """Plays audio from youtube (streamed, not downloaded)"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            self.queue.append(player)
            await ctx.send(get_response("add_queue", len=1))

            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)

    @commands.command()
    async def skip(self, ctx):
        """Skips current song and plays next in queue"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send(get_response("skip"))
        else:
            await ctx.send(get_response("not_playing"))

    @commands.command()
    async def queue(self, ctx):
        """Display queued songs"""
        if not self.queue:
            await ctx.send(get_response("queue_empty"))
        else:
            titles = [source.title for source in self.queue]
            queue_text = "\n".join(f"{i+1}. {title}" for i, title in enumerate(titles[:10]))
            await ctx.send(get_response("upcoming", queue_text=queue_text))

    @commands.command()
    async def clear(self, ctx):
        """Clear out remaining songs in queue"""
        self.queue.clear()
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        await ctx.send(get_response("queue_clear"))


    # adjust global volume if currently connected to voice
    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes music player volume"""

        if ctx.voice_client is None:
            return await ctx.send(get_response("not_connected"))

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(get_response("volume_changed", volume=volume))

    # dc bot
    @commands.command()
    async def stop(self, ctx):
        """Disconnect bot from voice"""

        await ctx.voice_client.disconnect()

    # guarantee bot readiness before running play() yt() or stream()
    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        """connects bot to author voice channel, unless author is not currently in voice"""
        
        print("ensure_voice triggered")
        print("Author voice:", ctx.author.voice)
        print("Voice client:", ctx.voice_client)

        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(get_response("not_connected"))
                raise commands.CommandError('Author not connected to a voice channel.')