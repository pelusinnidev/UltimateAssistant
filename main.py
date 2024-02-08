import discord
if not discord.opus.is_loaded():
  discord.opus.load_opus('libopus.so')
from discord.ext import commands

# 🤖 Bot setup with necessary intents 🛠️
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

ffmpeg_options = {
    'options': '-vn',  # No video, only audio 🎧
}

# 📚 "Database" of audios with local file paths 🎵
audios = {
    "Ambatukam": "Sounds/ambatukum.mp3",
    "BassDrop": "Sounds/bass drop sound effect.mp3",
    "BeastMode": "Sounds/Beast Mode Sound Effect | Soundboard Link 🔽🔽.mp3",
    "USA":
    "Sounds/USA Anthem but with gunshots, explosions, and eagle screeches.mp3",
    "OMAIGAJysus": "Sounds/OMAIGAJesus.mp3",
    # Add more audios here, ensuring the paths are correct 📁
}


@bot.event
async def on_ready():
  print(f'Bot connected as {bot.user} 🚀')


@bot.event
async def on_message(message):
  if message.author == bot.user or not message.guild:
    return  # Ignore bot's own messages and messages outside guilds 🙈

  if bot.user.mentioned_in(message) and message.mention_everyone is False:
    content = message.content.split()
    if len(content) == 1:
      await message.channel.send("Here's a list of available audios: " +
                                 ", ".join(audios.keys()))
    elif len(content) > 1 and content[1] in audios:
      audio_name = content[1]
      if message.author.voice:
        channel = message.author.voice.channel
        if message.guild.voice_client is None:
          await channel.connect(
          )  # Join the voice channel if not already connected 🎤
        voice_client = message.guild.voice_client
        async with message.channel.typing():
          # Play local file 🎼
          voice_client.play(
              discord.FFmpegPCMAudio(audios[audio_name], **ffmpeg_options))
          await message.channel.send(f"Playing {audio_name}... 🎧")
      else:
        await message.channel.send(
            "You must be in a voice channel to play an audio. 🚫🎙️")
    else:
      await message.channel.send(
          "I don't recognize that audio. Please choose one from the list. ❓")

  await bot.process_commands(message)  # Process other commands 🔄


@bot.command()
async def join(ctx):
  """Joins the user's voice channel. 🛬"""
  if ctx.author.voice:
    channel = ctx.author.voice.channel
    await channel.connect()
  else:
    await ctx.send("You must be in a voice channel to use this command. 🚫🎙️")


@bot.command()
async def leave(ctx):
  """Leaves the voice channel. 🛫"""
  voice_client = ctx.message.guild.voice_client
  if voice_client.is_connected():
    await voice_client.disconnect()
  else:
    await ctx.send("The bot is not in a voice channel. 🚫🔊")


# Replace YOUR_BOT_TOKEN with your actual bot token
bot.run('MTIwNDUxMDc1NjcwODY4MzgyNg.GWkHXR.2br2f7XRvRHUxzp-DZ8xUYlasn7OyTbvPliNWo')