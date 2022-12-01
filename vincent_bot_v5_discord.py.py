import discord
from discord import app_commands
from dotenv import load_dotenv
import os
import random
import json
from math import sqrt

version = "5"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

with open('data.json') as file:
    data = json.load(file)

print(data)

test_guild_id = 1013732206096699453

def nround(number):
    """Round a float to the nearest integer."""
    return int(number + 0.5)

# guilds = [discord.Object(id=1037308122265563176), discord.Object(id=1013732206096699453)]

class aclient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id=test_guild_id))
            self.synced = True
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        # emoijs_test =  disnake.Guild.emojis
        # print(str(emoijs_test))
        try:
            guild_emojis = list(message.guild.emojis)
        except AttributeError as e:
            # emoji = discord.utils.get(client.emojis, name='vincentsmile')
            guild_emojis = []
        # print(list(message.guild.emojis))
        guild_emojis_name_list = []
        for x in guild_emojis:
            if "vincent" in x.name:
                guild_emojis_name_list.append(x.name)
        if len(guild_emojis_name_list) == 0:
            guild_emojis_name_list.append(guild_emojis[0].name)
        # print(guild_emojis_name_list)
        user = message.author
        user_id = user.id
        user_id_str = str(user_id)
        guild_id = message.guild.id
        guild_id_str = str(guild_id)
        random_emoji = random.choice(guild_emojis_name_list)
        random_number = random.randint(1,8)
        if random_number == 1 or random_number == 2 or random_number == 3:
            emoji = discord.utils.get(client.emojis, name=random_emoji)
            await message.add_reaction(emoji)
        # emoji1 = discord.utils.get(client.emojis, name='vincentsmile')
        # emoji2 = discord.utils.get(client.emojis, name='vincentsmile2')
        # if random_number == 1:
        #     await message.add_reaction(emoji1)
        #     await message.add_reaction(emoji2)
        # elif random_number == 2:
        #     await message.add_reaction(emoji1)
        # elif random_number == 3:
        #     await message.add_reaction(emoji2)
        message_text = message.content
        message_text_lower = message_text.lower()
        # print(message_text)
        # if "vincent" in message_text:
        #     print("vincent detected")
        if user == client.user:
            return
        if "vincent" in message_text_lower:
            # sticker = discord.utils.get(client.stickers, name='Anata wa mō shinde iru')
            # print(sticker)
            await message.reply(file=discord.File('vincent.png'))
        elif "sad" in message_text_lower:
            await message.reply(file=discord.File('sad_vincent.png'))
        if len(message_text) > 5:
            # print(user_id)
            # print(type(user_id))
            # return
            if guild_id_str in data:
                if user_id_str in data[guild_id_str]:
                    data[guild_id_str][user_id_str]["xp"] += nround(sqrt(len(message_text)) - 1.45)
                else:
                    data[guild_id_str][user_id] = {"xp": nround(sqrt(len(message_text)) - 1.45)}
            else:
                data[guild_id_str] = {user_id_str:{"xp": nround(sqrt(len(message_text)) - 1.45)}}
            with open('data.json', "w") as file:
                json.dump(data, file)
                

client = aclient()
tree = app_commands.CommandTree(client=client)

@tree.command(name="about", description="Shows about page", guild = discord.Object(id=test_guild_id))
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f"This is the vincent bot, created to VINCENT\n\nVersion: {version}\nGithub: https://github.com/mikeee1/vincent-bot", ephemeral=True)

@tree.command(name="xp", description="Shows the amount of xp you have", guild = discord.Object(id=test_guild_id))
async def self(interaction: discord.Interaction):
    # print(interaction.guild.id)
    # print(str(interaction.guild.id))
    # print(str(interaction.user.id))
    try:
        await interaction.response.send_message(f"You have {data[str(interaction.guild.id)][str(interaction.user.id)]['xp']} xp")
    except KeyError as e:
        await interaction.response.send_message("Couldn't find your xp amount", ephemeral=True)


client.run(TOKEN)