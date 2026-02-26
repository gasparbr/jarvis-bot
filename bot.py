import discord
from discord.ext import commands
from dotenv import load_dotenv
from gtts import gTTS
import asyncio
import os
from openai import OpenAI

load_dotenv()
TOKEN = os.getenv("TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} online e consciente.")

@bot.command()
async def entrar(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("Jarvis conectado ao canal de voz.")
    else:
        await ctx.send("Entre em um canal de voz primeiro.")

@bot.command()
async def perguntar(ctx, *, pergunta):
    await ctx.send("Pensando...")

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é Jarvis, um assistente inteligente, educado e amigável."},
            {"role": "user", "content": pergunta}
        ]
    )

    texto = resposta.choices[0].message.content

    tts = gTTS(text=texto, lang="pt-br")
    tts.save("resposta.mp3")

    if ctx.voice_client is None:
        await ctx.invoke(entrar)

    ctx.voice_client.play(discord.FFmpegPCMAudio("resposta.mp3"))

    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)

    await ctx.send(texto)

bot.run(TOKEN)
