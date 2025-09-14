import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

import asyncio
import yt_dlp as youtube_dl

from responses import get_response

from collections import deque

load_dotenv()
token: str = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!'),
    description='Craig, a music bot that\'s not like, really into your music.',
    intents=intents,
)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)    

class YTDLSource(discord.PCMVolumeTransformer):
    """Turn youtube URL into volume regulated audio stream and metadata"""
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """Creates YTDL instance from URL"""
        # youtube_dl thread safety (ensure event loop available, run extract_info() in seperate thread)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        # temporary playlist handling (will expand to handle playlists later)
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)

        # deliver audio file with video disabled and metadata available
        return cls(discord.FFmpegPCMAudio(filename, options='-vn'), data=data)

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
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(get_response("not_connected"))
                raise commands.CommandError('Author not connected to a voice channel.')
                
@commands.command()
async def help(self, ctx):
    await ctx.send("help")

@bot.event
async def on_ready():
    assert bot.user is not None
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())