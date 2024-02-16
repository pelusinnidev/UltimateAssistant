import discord
from discord.ext import commands
import youtube_dl
import asyncio

# Configura youtube_dl per minimitzar l'ús de recursos
youtube_dl.utils.bug_reports_message = lambda: ''
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
ffmpeg_options = {
    'options': '-vn',
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

if not discord.opus.is_loaded():
  discord.opus.load_opus('libopus.so')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
bot = commands.Bot(
    command_prefix='!', intents=intents,
    help_command=None)  # Desactivem el comandament d'ajuda predeterminat

audios = {
    "LeclercNooo": "Sounds/leclercnoooooo.mp3",
    "LeaveaSpace": "Sounds/fernandoleavespace.mp3",
    "SuperMax": "Sounds/maxmaxmax.mp3",
}

destinacions_per_rol = {
    'Pilot': 'RacingChannel',
    'Spectator': 'SpectatorChannel',
}

canals_comunicats = {
    "oficial": "🗣-announcements",
    "fia": "🚩-fia",
}


def is_admin(user):
  return any(role.name == 'ADMIN' for role in user.roles)


@bot.event
async def on_ready():
  print(f'Bot connected as {bot.user}')


@bot.event
async def on_message(message):
  if message.author == bot.user or not message.guild or not bot.user.mentioned_in(
      message):
    return

  content = message.content.split()
  if len(content) < 2:
    return  # No hi ha accions o comandes especificades

  action = content[1].lower()
  args = content[2:]

  if is_admin(message.author):
    if action == 'audio':
      await play_audio(message, args)
    elif action == 'reunio':
      await reunio(message, args)
    elif action == 'announce':
      await announce(message, args)
    else:
      await message.channel.send("Comanda no reconeguda.")
  else:
    await message.channel.send(
        "No tens permisos per executar aquesta acció o la comanda no existeix."
    )

  await bot.process_commands(message)


async def play_audio(message, args):
  if not args:
    await message.channel.send(
        "Especifica un àudio per reproduir. Exemple: @Bot audio LeclercNooo")
    return

  query = ' '.join(args)
  if query not in audios:
    await message.channel.send(
        "Audio not found. Please use a valid audio name.")
    return

  voice_channel = message.author.voice.channel
  if voice_channel:
    vc = await voice_channel.connect(
    ) if not message.guild.voice_client else message.guild.voice_client
    vc.stop()
    source = discord.FFmpegPCMAudio(audios[query], **ffmpeg_options)
    vc.play(source,
            after=lambda e: print(f"Finished playing: {query}. Error: {e}"
                                  if e else ""))
    await message.channel.send(f"Playing {query}...")
  else:
    await message.channel.send(
        "You need to be in a voice channel to play audio.")


async def reunio(message, args):
  if not args:
    await message.channel.send(
        "Especifica un URL de vídeo per iniciar la carrera. Exemple: @Bot reunio <url>"
    )
    return

  url = args[0]
  # Aquesta secció necessitaria una implementació específica que es detalla a continuació


async def announce(message, args):
  if len(args) < 2:
    await message.channel.send(
        "Format incorrecte. Exemple: @Bot announce oficial Missatge important")
    return

  tipus = args[0].lower()
  missatge_text = ' '.join(args[1:])
  # Aquesta secció necessitaria una implementació específica que es detalla a continuació


# Implementa les funcions reunio i announce segons les teves necessitats específiques.

# Continuació del codi anterior...


async def reunio(message, args):
  if not args:
    await message.channel.send(
        "Especifica un URL de vídeo per iniciar la carrera. Exemple: @Bot reunio <url>"
    )
    return

  url = args[0]
  canal_reunio = discord.utils.get(message.guild.voice_channels,
                                   name='CanalReunio')
  if not canal_reunio:
    await message.channel.send("Canal de reunió no trobat.")
    return

  # Asumim que els rols ja estan definits en destinacions_per_rol
  membres_amb_rols = []
  for rol_name, channel_name in destinacions_per_rol.items():
    rol = discord.utils.get(message.guild.roles, name=rol_name)
    if rol:
      membres_amb_rols += [membre for membre in rol.members if membre.voice]

  if membres_amb_rols:
    for membre in membres_amb_rols:
      await membre.move_to(canal_reunio)
    await asyncio.sleep(1)  # Dona temps per a que tots es moguin

  if not message.guild.voice_client:
    await canal_reunio.connect()
  voice_client = message.guild.voice_client

  with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
    info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']
    voice_client.play(discord.FFmpegPCMAudio(URL, **ffmpeg_options))
    await message.channel.send(f"Reproduint vídeo: {info['title']}")

  # Espera a que el vídeo acabi abans de moure els usuaris de nou
  while voice_client.is_playing():
    await asyncio.sleep(1)

  for membre in membres_amb_rols:
    for rol_name, channel_name in destinacions_per_rol.items():
      if rol_name in [rol.name for rol in membre.roles]:
        desti_canal = discord.utils.get(message.guild.voice_channels,
                                        name=channel_name)
        await membre.move_to(desti_canal)
        break

  await voice_client.disconnect()


async def announce(message, args):
  if len(args) < 2:
    await message.channel.send(
        "Format incorrecte. Exemple: @Bot announce oficial 'Missatge important'"
    )
    return

  tipus, *missatge_text = args
  missatge_text = ' '.join(missatge_text)
  canal_nom = canals_comunicats.get(tipus.lower())
  if not canal_nom:
    await message.channel.send("Tipus de comunicat desconegut.")
    return

  canal = discord.utils.get(message.guild.text_channels, name=canal_nom)
  if not canal:
    await message.channel.send(f"Canal de comunicat '{canal_nom}' no trobat.")
    return

  embed = discord.Embed(title=f"Comunicat {tipus.upper()}",
                        description=missatge_text,
                        color=0x00ff00)
  await canal.send(embed=embed)
  await message.channel.send(
      f"Comunicat {tipus.upper()} enviat a {canal.mention}.")


# Recordatori per substituir 'YOUR_BOT_TOKEN' amb el token real del teu bot
bot.run(
    'MTE2MzgyMzQ3MzQ0MTkwMjU5Mg.GKov4a.dwd7Y7GB7Sd0HXI5XP7tdG5Ljxm3XwgK3T6g5A')
