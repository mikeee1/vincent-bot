import os

import discord
from dotenv import load_dotenv
import logging
from time import sleep
import random
from discord import app_commands

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# class MyClient(discord.Client):
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        await tree.sync(guild=discord.Object(id=1013732206096699453))
        print("2")
    
    async def on_message(self, message):
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
                





intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN, log_handler=handler)

tree = app_commands.CommandTree(client)

@tree.command(name = "commandname", description = "My first application Command", guild=discord.Object(id=1013732206096699453)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds. 1013732206096699453
async def first_command(interaction):
    await interaction.response.send_message("Hello!")