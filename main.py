import discord
from discord.ext import commands
import youtube_dl
import asyncio

if not discord.opus.is_loaded():
    discord.opus.load_opus('libopus.so')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

audios = {
    "LeclercNooo": "Sounds/leclercnoooooo.mp3",
    "LeaveaSpace": "Sounds/fernandoleavespace.mp3",
    "SuperMax": "Sounds/maxmaxmax.mp3", 
}

videos = {
    "EpicRace": "https://www.youtube.com/watch?v=example1",
    "FunnyMoments": "https://www.youtube.com/watch?v=example2",
    "GreatOvertakes": "https://www.youtube.com/watch?v=example3",
}

destinacions_per_rol = {
    'Pilot': 'RacingChannel',
    'Spectator': 'SpectatorChannel',
}

canals_comunicats = {
    "oficial": "CanalOficial",
    "fia": "CanalFIA",
}

def is_admin():
    def predicate(ctx):
        return any(role.name == 'ADMIN' for role in ctx.author.roles)
    return commands.check(predicate)

async def moure_usuaris_a_canal(membres, canal_desti):
    for membre in membres:
        try:
            if membre.voice:
                await membre.move_to(canal_desti)
        except discord.HTTPException:
            continue

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user or not message.guild:
        return
    
    ctx = await bot.get_context(message)
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        if is_admin()(ctx):
            await message.channel.send(
                "Ets un ADMIN! Aquí tens les teves opcions:\n"
                "- `!play <nom_audio>`: Reprodueix un àudio.\n"
                "- `!reunio <url_video>`: Inicia una carrera.\n"
                "- `!announce <tipus> <missatge>`: Envia un comunicat.\n"
                "Llista d'audios disponibles: " + ", ".join(audios.keys())
            )
        else:
            await message.channel.send(
                "Hola! Aquí tens una llista dels audios disponibles: " + ", ".join(audios.keys())
            )
    await bot.process_commands(message)

@bot.command()
async def play(ctx, *, query: str):
    if query not in audios:
        await ctx.send("Audio not found. Please use a valid audio name.")
        return
    
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        if ctx.guild.voice_client is None:
            await channel.connect()
        voice_client = ctx.guild.voice_client
        voice_client.stop()
        source = discord.FFmpegPCMAudio(audios[query], **ffmpeg_options)
        voice_client.play(source, after=lambda e: print(f"Finished playing: {query}. Error: {e}" if e else ""))
        await ctx.send(f"Playing {query}...")
    else:
        await ctx.send("You need to be in a voice channel to play audio.")

@bot.command()
@is_admin()
async def reunio(ctx, url: str):
    await ctx.send("Starting race sequence...")
    canal_reunio = discord.utils.get(ctx.guild.voice_channels, name='RaceChannel')  # Change to the actual channel name
    if canal_reunio is None:
        await ctx.send("Race channel not found.")
        return
    
    membres = [membre for membre in ctx.guild.members if any(rol.name in destinacions_per_rol for rol in membre.roles)]
    await moure_usuaris_a_canal(membres, canal_reunio)
    
    if ctx.guild.voice_client is None:
        await canal_reunio.connect()
    voice_client = ctx.guild.voice_client
    
    with youtube_dl.YoutubeDL({'format': 'bestaudio'}) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(URL, **ffmpeg_options), after=lambda e: print("Race video finished."))
        await ctx.send(f"Playing race video: {info['title']}")
    
    await asyncio.sleep(1)  # Adjust sleep time according to the video length
    while voice_client.is_playing():
        await asyncio.sleep(1)  # Keep the command running until the video is finished
    
    for membre in membres:
        for rol in membre.roles:
            if rol.name in destinacions_per_rol:
                canal_desti = discord.utils.get(ctx.guild.voice_channels, name=destinacions_per_rol[rol.name])
                await moure_usuaris_a_canal([membre], canal_desti)
                break
    
    if voice_client.is_connected():
        await voice_client.disconnect()
    await ctx.send("Race sequence completed.")

@bot.command()
@is_admin()
async def announce(ctx, tipus: str, *, missatge: str):
    if tipus.lower() not in canals_comunicats:
        await ctx.send("Tipus de comunicat desconegut.")
        return

    canal_nom = canals_comunicats[tipus.lower()]
    canal = discord.utils.get(ctx.guild.text_channels, name=canal_nom)
    if canal:
        embed = discord.Embed(title=f"Comunicat {tipus.upper()}", description=missatge, color=0x00ff00)
        # Pots afegir una imatge a l'embed si ho desitges
        # embed.set_image(url="URL_DE_LA_IMATGE")
        await canal.send(embed=embed)
        await ctx.send(f"Comunicat {tipus.upper()} enviat correctament.")
    else:
        await ctx.send("Canal de comunicat no trobat.")

# No oblideu substituir 'YOUR_BOT_TOKEN' amb el token real del vostre bot
bot.run('YOUR_BOT_TOKEN')