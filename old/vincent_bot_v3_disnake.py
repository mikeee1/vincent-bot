import os

import disnake
from dotenv import load_dotenv
import logging
from time import sleep
import random
# from discord import app_commands
from disnake.ext import commands

# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# class MyClient(discord.Client):
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# bot = commands.InteractionBot(test_guilds=[1013732206096699453])

class MyClient(disnake.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
    
    async def on_message(self, message):
        # emoijs_test =  disnake.Guild.emojis
        # print(str(emoijs_test))
        random_number = random.randint(1,8)
        emoji1 = disnake.utils.get(client.emojis, name='vincentsmile')
        emoji2 = disnake.utils.get(client.emojis, name='vincentsmile2')
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
            await message.reply(file=disnake.File('vincent.png'))
        elif "sad" in message_text:
            await message.reply(file=disnake.File('sad_vincent.png'))
                




intents = disnake.Intents.default()
intents.message_content = True
# intents.

client = MyClient(intents=intents)
client.run(TOKEN)


command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

bot = commands.Bot(
    command_prefix='!',
    test_guilds=[1013732206096699453,1037308122265563176], # Optional
    command_sync_flags=command_sync_flags,
)

# bot = commands.Bot(
#     # command_prefix = "!",
#     test_guilds = [1013732206096699453,1037308122265563176],
#     sync_commands_debug = True
# )

@bot.slash_command(description="test please ignore", name="ping")
async def ping(inter: disnake.ApplicationCommandInteraction):
    print("pong")
    await inter.response.send_message("Pong!")

print("test")