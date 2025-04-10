import discord
from config import config

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    # Check if the message is a DM and not from the bot itself
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        await message.channel.send("hi")

bot.run(config['discord_token'])