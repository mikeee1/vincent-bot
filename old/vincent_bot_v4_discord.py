import os

import discord
from dotenv import load_dotenv
import logging
from time import sleep
import random
# from discord import app_commands
# from disnake.ext import commands
from discord import app_commands

# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# class MyClient(discord.Client):
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# bot = commands.InteractionBot(test_guilds=[1013732206096699453])

class MyClient(discord.Client):
    # def __init__(self, intents):
    #     super().__init__(intents=intents)
    #     self.synced = False

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        # await self.wait_until_ready()
        # if not self.synced:
        #     await tree.sync(guild=discord.Object(id=1013732206096699453))
        #     self.synced = True
            
    
    async def on_message(self, message):
        # emoijs_test =  disnake.Guild.emojis
        # print(str(emoijs_test))
        random_number = random.randint(1,8)
        emoji1 = discord.utils.get(client.emojis, name='vincentsmile')
        emoji2 = discord.utils.get(client.emojis, name='vincentsmile2')
        if random_number == 1:
            await message.add_reaction(emoji1)
            await message.add_reaction(emoji2)
        elif random_number == 2:
            await message.add_reaction(emoji1)
        elif random_number == 3:
            await message.add_reaction(emoji2)
        message_text = message.content
        message_text = message_text.lower()
        if "vincent" in message_text:
            # sticker = discord.utils.get(client.stickers, name='Anata wa mō shinde iru')
            # print(sticker)
            await message.reply(file=discord.File('vincent.png'))
        elif "sad" in message_text:
            await message.reply(file=discord.File('sad_vincent.png'))
        message_text = ""
        if message_text.startswith("!about"):
            pass
                




intents = discord.Intents.default()
intents.message_content = True
# intents.

client = MyClient(intents=intents)
client.run(TOKEN)

# tree = app_commands.CommandTree(client=client)

# @tree.command(guild=discord.Object(id=1037308122265563176), name="ping", description="test")
# async def slash(interaction: discord.Integration):
#     await interaction.response.send_message("pong")

