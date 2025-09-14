import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

import asyncio

from responses import get_response
from music import Music

load_dotenv()
token: str = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!'),
    description='Craig, a music bot that\'s not like, really into your music.',
    intents=intents,
)

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