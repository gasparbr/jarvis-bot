import discord
from discord.ext import commands
from dotenv import load_dotenv
from gtts import gTTS
import asyncio
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} online!")

@bot.command()
async def entrar(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("Conectado ao canal de voz.")
    else:
        await ctx.send("Entre em um canal de voz primeiro.")

@bot.command()
async def sair(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Saindo do canal.")

@bot.command()
async def falar(ctx, *, texto):
    if ctx.voice_client is None:
        await ctx.send("Use !entrar primeiro.")
        return

    tts = gTTS(text=texto, lang="pt-br")
    tts.save("voz.mp3")

    ctx.voice_client.play(discord.FFmpegPCMAudio("voz.mp3"))

    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)

bot.run(TOKEN)
