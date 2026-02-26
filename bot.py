import discord
from discord.ext import commands
from dotenv import load_dotenv
from gtts import gTTS
import asyncio
import os
from groq import Groq
import whisper
import wave

load_dotenv()
TOKEN = os.getenv("TOKEN")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# carregar whisper (modelo leve e grátis)
model = whisper.load_model("base")

# ----------- VOICE SINK -----------
class AudioSink(discord.sinks.WaveSink):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    async def finished_callback(self, sink, channel):
        for user_id, audio in sink.audio_data.items():
            filename = f"audio/{user_id}.wav"
            with open(filename, "wb") as f:
                f.write(audio.file.getbuffer())

            # TRANSCRIÇÃO
            result = model.transcribe(filename)
            pergunta = result["text"]

            await self.ctx.send(f"Você disse: {pergunta}")

            # IA RESPONDE
            resposta = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Você é Jarvis, um assistente inteligente e amigável."},
                    {"role": "user", "content": pergunta}
                ]
            )

            texto = resposta.choices[0].message.content

            # TTS
            tts = gTTS(text=texto, lang="pt-br")
            tts.save("resposta.mp3")

            vc = self.ctx.voice_client
            vc.play(discord.FFmpegPCMAudio("resposta.mp3"))

            while vc.is_playing():
                await asyncio.sleep(1)

            await self.ctx.send(texto)


@bot.event
async def on_ready():
    print(f"{bot.user} online e ouvindo você.")


@bot.command()
async def entrar(ctx):
    if not ctx.author.voice:
        await ctx.send("Entre em um canal de voz primeiro.")
        return

    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send("Jarvis entrou e está te ouvindo 👂")


@bot.command()
async def ouvir(ctx):
    vc = ctx.voice_client
    if vc is None:
        await ctx.send("Eu preciso estar no canal de voz primeiro.")
        return

    sink = AudioSink(ctx)
    vc.start_recording(
        sink,
        sink.finished_callback,
        ctx.channel,
    )

    await ctx.send("Pode falar! Estou ouvindo por 10 segundos...")

    await asyncio.sleep(10)
    vc.stop_recording()


bot.run(TOKEN)
