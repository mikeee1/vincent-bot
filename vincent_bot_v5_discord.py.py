import discord
from discord import app_commands
from dotenv import load_dotenv
import os
import random
import json
from math import sqrt
import time

version = "5"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

with open('data.json') as file:
    data = json.load(file)

with open('settings.json') as file:
    settings = json.load(file)

# if len(settings) == 0:
#     settings["cooldown"] = 5
#     with open('settings.json', "w") as file:
#         json.dump(settings, file)

print(data)

test_guild_id = 1037308122265563176
cooldown_dict = {}

def nround(number):
    """Round a float to the nearest integer."""
    return int(number + 0.5)

# guilds = [discord.Object(id=1037308122265563176), discord.Object(id=1013732206096699453)]

class aclient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id=test_guild_id))
            self.synced = True
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        # print(message.content)
        # emoijs_test =  disnake.Guild.emojis
        # print(str(emoijs_test))
        try:
            guild_emojis = list(message.guild.emojis)
            guild_emojis_name_list = []
            for x in guild_emojis:
                if "vincent" in x.name:
                    guild_emojis_name_list.append(x.name)
            if len(guild_emojis_name_list) == 0:
                guild_emojis_name_list.append(guild_emojis[0].name)
        except AttributeError as e:
            # emoji = discord.utils.get(client.emojis, name='vincentsmile')
            guild_emojis = [discord.utils.get(client.emojis, name="thumbsup")]
        # print(list(message.guild.emojis))
        # print(guild_emojis_name_list)
        user = message.author
        user_id = user.id
        user_id_str = str(user_id)
        if user == client.user:
            return
        
        guild_id = message.guild.id
        guild_id_str = str(guild_id)

        if not guild_id_str in settings:
            settings[guild_id_str] = {"cooldown": 5}
            with open('settings.json', "w") as file:
                json.dump(settings, file)

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
        
        
        if "vincent" in message_text_lower:
            # sticker = discord.utils.get(client.stickers, name='Anata wa mō shinde iru')
            # print(sticker)
            await message.reply(file=discord.File('vincent.png'))
        elif "sad" in message_text_lower:
            await message.reply(file=discord.File('sad_vincent.png'))
        if guild_id_str in cooldown_dict:
            if user_id_str in cooldown_dict[guild_id_str]:
                last_time_user_send_message = cooldown_dict[guild_id_str][user_id_str]
                # print(f'Variable: {last_time_user_send_message}, Type: {type(last_time_user_send_message)}')
                # print(f'Variable: {settings[guild_id_str]["cooldown"]}, Type: {type(settings[guild_id_str]["cooldown"])}')
                # print(f'Variable: {time.time()}, Type: {type(time.time())}')
                if last_time_user_send_message + settings[guild_id_str]["cooldown"] <= time.time():
                    # print("xp given")
                    cooldown_dict[guild_id_str][user_id_str] = time.time()
                    pass
                else:
                    # print("xp not given")
                    return
            else:
                cooldown_dict[guild_id_str][user_id_str] = time.time()
        else:
            cooldown_dict[guild_id_str] = {user_id_str: time.time()}
        # print(json.dumps(cooldown_dict, indent=4, sort_keys=False))
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
                


# bot = discord.Bot()
client = aclient()
tree = app_commands.CommandTree(client=client)

# @bot.slash_command(guild_ids=[test_guild_id])
# async def test(ctx):
#     await ctx.respond("test")

@tree.command(name="about", description="Shows about page", guild = discord.Object(id=test_guild_id))
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f"This is the vincent bot, created to VINCENT\n\nVersion: {version}\nGithub: https://github.com/mikeee1/vincent-bot", ephemeral=True)

@tree.command(name="xp", description="Shows the amount of xp you have", guild = discord.Object(id=test_guild_id))
async def self(interaction: discord.Interaction):
    # print(interaction.guild.id)
    # print(str(interaction.guild.id))
    # print(str(interaction.user.id))
    try:
        await interaction.response.send_message(f"<@{str(interaction.user.id)}> has {data[str(interaction.guild.id)][str(interaction.user.id)]['xp']} xp")
    except KeyError as e:
        await interaction.response.send_message("Couldn't find your xp amount", ephemeral=True)

@tree.command(name="cooldown", description="cooldown commands", guild = discord.Object(id=test_guild_id))
# @tree.command.default_permissions()
@app_commands.checks.has_permissions(administrator=True)
@app_commands.default_permissions(administrator=True)
async def self(interaction: discord.Interaction, set_get: str, amount: float):
    if set_get.lower() == "set":
        settings[str(interaction.guild.id)]['cooldown'] = amount
        with open('settings.json', "w") as file:
            json.dump(settings, file)
        # print("set")
        await interaction.response.send_message(f"The cooldown in now {settings[str(interaction.guild.id)]['cooldown']} seconds", ephemeral=True)
        pass
    elif set_get.lower() == "get":
        # print("get")
        await interaction.response.send_message(f"The cooldown is {settings[str(interaction.guild.id)]['cooldown']} seconds", ephemeral=True)

    
    # print(interaction.guild.id)
    # print(str(interaction.guild.id))
    # print(str(interaction.user.id))
    # if not interaction
    # pass

@tree.command(name="xpget", description="Shows the amount of xp someone has", guild = discord.Object(id=test_guild_id))
async def self(interaction: discord.Interaction, user: discord.Member):
    print(user)
    split_user = str(user).split("#")
    # print(f'Variable: {interaction.guild.id}, Type: {type(interaction.guild.id)}')
    guild_id = interaction.guild.id
    guild = client.get_guild(guild_id)
    # print(guild)
    # print(split_user)
    user = discord.utils.get(guild.members, name = split_user[0], discriminator = split_user[1])
    # print(user.id)
    # print(data[str(interaction.guild.id)])
    # print(data[str(interaction.guild.id)][str(user.id)])
    # print(data[str(interaction.guild.id)][str(user.id)]['xp'])
    try:
        await interaction.response.send_message(f"{user} has {data[str(interaction.guild.id)][str(user.id)]['xp']} xp", ephemeral=True)
    except KeyError as e:
        await interaction.response.send_message(f"Couldn't find {user} xp amount", ephemeral=True)



@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("no permissions", ephemeral=True)

client.run(TOKEN)