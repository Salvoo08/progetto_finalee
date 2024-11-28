import discord
from discord.ext import commands
import os
from web_scraper import read_model

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Siamo loggati come {bot.user}')

@bot.command()
async def ciao(ctx):
    await ctx.send(f'Ciao! Sono RiepilogoMaster {bot.user}!')

@bot.command()
async def ripeti(ctx, numero_ripeti: int = 5):
    if numero_ripeti > 20:
        numero_ripeti = 20  # Limite massimo per sicurezza
    await ctx.send("he" * numero_ripeti)

@bot.command()
async def riepiloga_pagina(ctx, url: str):
    summary, key_topics, message = read_model(url)
    if summary and key_topics:
        await ctx.send(f"Riassunto della pagina:\n{summary}\n\nArgomenti principali:\n{key_topics}\n\n{message}")
    else:
        await ctx.send(message)

@bot.command()
async def chiedi_riepilogo(ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ["sì", "si", "no"]

    await ctx.send("Vuoi che faccia un riassunto di una pagina web? (Rispondi 'sì' o 'no')")

    try:
        msg = await bot.wait_for("message", check=check, timeout=30)
        if msg.content.lower() in ["sì", "si"]:
            await ctx.send("Perfetto! Per favore, fornisci l'URL della pagina web.")
            
            url_msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
            await riepiloga_pagina(ctx, url_msg.content)
        else:
            await ctx.send("Va bene, fammi sapere se hai bisogno di altro. Ciao!")
    except TimeoutError:
        await ctx.send("Tempo scaduto. Per favore, riprova.")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f'Si è verificato un errore: {error}')

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
