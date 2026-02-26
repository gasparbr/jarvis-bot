import discord
from discord.ext import commands
from dotenv import load_dotenv
from gtts import gTTS
import asyncio
import os
from groq import Groq

load_dotenv()
TOKEN = os.getenv("TOKEN")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} online e consciente.")

@bot.command()
async def entrar(ctx):
    if not ctx.author.voice:
        await ctx.send("Entre em um canal de voz primeiro.")
        return

    channel = ctx.author.voice.channel

    # Se já estiver conectado, desconecta primeiro
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await asyncio.sleep(1)

    try:
        await channel.connect(reconnect=True, timeout=60)
        await ctx.send("Jarvis conectado ao canal de voz.")
    except Exception:
        await ctx.send("Tive dificuldade para conectar... tentando novamente.")
        await asyncio.sleep(2)
        await channel.connect(reconnect=True, timeout=60)

@bot.command()
async def perguntar(ctx, *, pergunta):
    await ctx.send("Aura está Pensando...")

    resposta = client.chat.completions.create(
        model="llama-3.1-8b-instant",
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
