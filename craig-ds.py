import discord
import os
from dotenv import load_dotenv

import asyncio
import youtube_dl

load_dotenv()

token: str = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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

@client.event
async def on_ready() -> None:
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message) -> None:
    if message.author == client.user:
        return
    
    if message.content.startswith('$hello'):
        await message.channel.send("Hello!")

client.run(token)