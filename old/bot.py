import os
from discord.utils import get
import discord
from dotenv import load_dotenv
import logging
from time import sleep

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# class MyClient(discord.Client):
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
# intents.message_content = True
client = discord.Client(intents=intents)
# client = MyClient(intents=intents)
# client.run(TOKEN, log_handler=handler)

@client.event
async def on_ready():
    print('Ready!')

@client.event
async def on_message(message):
    emoji = discord.utils.get(client.emojis, name='vincentsmile')
    await message.add_reaction(emoji)
    emoji = discord.utils.get(client.emojis, name='vincentsmile2')
    await message.add_reaction(emoji)
    

client.run(TOKEN)