import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import tasks
from dotenv import load_dotenv
import os
import random
import json
from math import sqrt
import time
from PIL import Image, ImageFont, ImageDraw
import requests
import logging
import typing
import shutil
from datetime import datetime
# from bs4 import BeautifulSoup


MAX_FILE_SIZE = 8000000
GAME_NOTIFIER_LOOP_SECONDS = 600
log_file_name = "discord.log"
log_file_name_debug = "discord_debug.log"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


fh = logging.FileHandler(log_file_name, mode="w", encoding='utf-8')
fh.setLevel(logging.INFO)

fhd = logging.FileHandler(log_file_name_debug, mode="w", encoding='utf-8')
fhd.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)d] %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
fhd.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)
logger.addHandler(fhd)


version = "5.5.14"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BOT_ADMIN_ID = int(os.getenv('BOT_ADMIN_ID'))

with open('data.json') as file:
    data = json.load(file)

with open('settings.json') as file:
    settings = json.load(file)

with open('free_games.json') as file:
    free_games = json.load(file)

if not os.path.exists("free_games.log"):
    open("free_games.log", "x").close()

# if len(settings) == 0:
#     settings["cooldown"] = 5
#     with open('settings.json', "w") as file:
#         json.dump(settings, file)

# print(data)

# test_guild_id = 1048917571270873109
cooldown_dict = {}

def nround(number: float | int) -> int:
    """Round a float to the nearest integer."""
    return int(number + 0.5)

def xp_formula(message_text: str) -> int:
    return nround(sqrt(0.9*len(message_text)) - 1.45)

def level_formula(xp: int) -> int:
    return 0.002 * xp

def level_formula_inverse(level: int) -> int:
    return 500 * level

def calculate_progress(guild_id: int, user_id: int) -> float:
    try:
        current_xp = data[guild_id][user_id]['xp']
        current_level = data[guild_id][user_id]['level']
    except KeyError:
        current_xp = 0
        current_level = 0
    xp_next_level = level_formula_inverse(current_level+1)
    xp_current_level = level_formula_inverse(current_level)
    # xp_fraction = (current_xp-xp_current_level)/xp_next_level
    xp_fraction =  (current_xp - xp_current_level) / (xp_next_level - xp_current_level)
    # print(xp_fraction)
    return xp_fraction


def drawProgressBar(d, x, y, w, h, progress, bg="gray", fg="green"):
    # draw background
    d.ellipse((x+w, y, x+h+w, y+h), fill=bg)
    d.ellipse((x, y, x+h, y+h), fill=bg)
    d.rectangle((x+(h/2), y, x+w+(h/2), y+h), fill=bg)

    # draw progress bar
    w *= progress
    d.ellipse((x+w, y, x+h+w, y+h),fill=fg)
    d.ellipse((x, y, x+h, y+h),fill=fg)
    d.rectangle((x+(h/2), y, x+w+(h/2), y+h),fill=fg)

    return d


def create_xp_image(data, user_avatar, user_name_list, user_id, guild_id, user_name, file_name, rank):
    if user_avatar == None:
        avatar_number = int(user_name_list[1]) % 5
        avatar_url = f"https://cdn.discordapp.com/embed/avatars/{avatar_number}.png"
    else:
        avatar_url = str(user_avatar)
    avatar = requests.get(avatar_url).content
    # print(str(interaction.user.avatar).split("?")[0])
    with open(user_id+".png", "wb") as file:
        file.write(avatar)
    xp_image = Image.new(mode="RGB", size=(800, 200))
    draw = ImageDraw.Draw(xp_image)
    font_60 = ImageFont.truetype("arial.ttf", size=60)
    font_50 = ImageFont.truetype("arial.ttf", size=50)
    font_40 = ImageFont.truetype("arial.ttf", size=40)
    font_30 = ImageFont.truetype("arial.ttf", size=30)
    draw.rounded_rectangle(xy=[0,0, 800,200], radius = 20, fill=(0,0,0,255))
    avatar_image = Image.open(user_id+".png")
    avatar_image = avatar_image.resize(size=(160,160))
    xp_image.paste(avatar_image, (20,20))
    # draw.rounded_rectangle(xy=[20,20, 180,180], radius=30, outline=(0,0,0,255), width=20)
    try:
        draw = drawProgressBar(d = draw, x = 200, y = 140, w = 520, h = 40, progress = calculate_progress(guild_id, user_id))
        xp_text = f"{data[guild_id][user_id]['xp']}/{level_formula_inverse(data[guild_id][user_id]['level']+1)} XP"
    except KeyError:
        draw = drawProgressBar(d = draw, x = 200, y = 140, w = 520, h = 40, progress = 0)
        xp_text = f"0/500 XP"
    draw.text((215, 95), text=xp_text, fill="gray", font=font_40)
    draw.text((215, 20), text=str(user_name), fill="gray", font=font_30)
    draw.text((630, 105), text="Level", fill="gray", font=font_30)
    try:
        draw.text((705, 80), text=str(data[guild_id][user_id]['level']), fill="gray", font=font_60)
    except KeyError:
        draw.text((705, 80), text="0", fill="gray", font=font_60)
    if rank is not None:
        draw.text((685, 20), text="#", fill="gray", font=font_30)
        draw.text((705, 3), text=str(rank), fill="gray", font=font_50)
    xp_image.save(file_name)
    os.remove(str(user_id)+".png")

def calculate_rank(user_id, guild_id) -> int:
    rank_list = []
    for x in data[guild_id].keys():
        rank_list.append(data[guild_id][x]["xp"])
    # print(rank_list)
    rank_list = list(set(rank_list))
    rank_list.sort(reverse=True)
    # print(rank_list)
    rank = rank_list.index(data[guild_id][user_id]["xp"])+1
    # print(rank)
    return rank

def replacer(s, newstring, index, nofail=False):
    # raise an error if index is outside of the string
    if not nofail and index not in range(len(s)):
        raise ValueError("index outside given string")

    # if not erroring, but the index is still not in the correct range..
    if index < 0:  # add it to the beginning
        return newstring + s
    if index > len(s):  # add it to the end
        return s + newstring

    # insert the new string between "slices" of the original
    return s[:index] + newstring + s[index + 1:]


# guilds = [discord.Object(id=1037308122265563176), discord.Object(id=1013732206096699453)]

class aclient(discord.Client):
    def __init__(self):
        global activity
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True
        intents.guild_reactions = True
        activity = discord.Activity(type = discord.ActivityType.watching, name = "out for Vincent", details="Time until refresh")
        super().__init__(intents=intents, activity = activity)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        # activity = discord.Activity(type = discord.ActivityType.watching, name = "out for Vincent")
        # await client.change_presence(activity = activity)
        logging.info(f'Logged on as {self.user}!')
        # print(f'Logged on as {self.user}!')
        check_for_deals.start()

    async def on_message(self, message):
        message_text = message.content
        message_text_lower = message_text.lower()
        if isinstance(message.channel, discord.channel.DMChannel):
            if message.author.id == BOT_ADMIN_ID:
                if message_text.startswith("!"):
                    command_list = message_text[1:].split(" ")
                    if command_list[0] == "stop" or command_list[0] == "quit":
                        await message.reply("Shutting down")
                        quit()
                    elif command_list[0] == "log":
                        if len(command_list) == 1:
                            # with open(log_file_name, "r") as file:
                            #     log_data = file.read()
                            # if len(log_data) > 2000:
                            #     to_much = len(log_data) - 2000
                            #     await message.reply(log_data[to_much:])
                            # else:
                            #     await message.reply(log_data)
                            # print(f'Variable: {os.path.getsize(log_file_name)}, Type: {type(os.path.getsize(log_file_name))}')
                            file_size = os.path.getsize(log_file_name)
                            if  file_size < MAX_FILE_SIZE:
                                await message.reply(file=discord.File(log_file_name))
                            else:
                                await message.reply(f"File to big: {file_size}")
                        elif len(command_list) == 2:
                            if command_list[1] == "debug":
                                # with open(log_file_name_debug, "r") as file:
                                #     log_data = file.read()
                                # if len(log_data) > 2000:
                                #     to_much = len(log_data) - 2000
                                #     await message.reply(log_data[to_much:])
                                # else:
                                #     await message.reply(log_data)
                                file_size = os.path.getsize(log_file_name_debug)
                                if file_size < MAX_FILE_SIZE:
                                    await message.reply(file=discord.File(log_file_name_debug))
                                else:
                                    await message.reply(f"File to big: {file_size}")
                            elif command_list[1] == "txt":
                                with open(log_file_name, "r", encoding="utf-8") as file:
                                    log_data = file.read()
                                if len(log_data) > 2000:
                                    to_much = len(log_data) - 2000
                                    await message.reply(log_data[to_much:])
                                else:
                                    await message.reply(log_data)
                        elif len(command_list) == 3:
                            if command_list[1] == "debug" and command_list[2] == "txt":
                                with open(log_file_name_debug, "r", encoding="utf-8") as file:
                                    log_data = file.read()
                                if len(log_data) > 2000:
                                    to_much = len(log_data) - 2000
                                    await message.reply(log_data[to_much:])
                                else:
                                    await message.reply(log_data)
                    elif command_list[0] == "dump":
                        if command_list[1] == "data":
                            if len(command_list) == 2:
                                await message.reply(json.dumps(data, indent=4))
                            elif command_list[2] == "raw":
                                await message.reply(data)
                        elif command_list[1] == "settings":
                            if len(command_list) == 2:
                                await message.reply(json.dumps(settings, indent=4))
                            elif command_list[2] == "raw":
                                await message.reply(settings)
                        elif command_list[1] == "cooldown":
                            if len(command_list) == 2:
                                await message.reply(json.dumps(cooldown_dict, indent=4))
                            elif command_list[2] == "raw":
                                await message.reply(cooldown_dict)
                        elif command_list[1] == "free_games":
                            if len(command_list) == 2:
                                await message.reply(json.dumps(free_games, indent=4))
                            elif command_list[2] == "raw":
                                await message.reply(free_games)
                        
                    
            return
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
        # print(user.avatar)

        user_id = user.id
        user_id_str = str(user_id)
        if user == client.user:
            return
        
        guild_id = message.guild.id
        guild_id_str = str(guild_id)

        if not guild_id_str in settings:
            settings[guild_id_str] = {"cooldown": 5.0, "games_notifier": False}
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
                    data[guild_id_str][user_id_str]["xp"] += xp_formula(message_text)
                else:
                    data[guild_id_str][user_id_str] = {"version": version, "xp": xp_formula(message_text), "level": 0}
            else:
                data[guild_id_str] = {user_id_str:{"version": version, "xp": xp_formula(message_text), "level": 0}}


            level = data[guild_id_str][user_id_str]["level"]
            xp = data[guild_id_str][user_id_str]["xp"]
            if xp >= level_formula_inverse(level+1):
                data[guild_id_str][user_id_str]["level"] += 1
                await message.reply(f"congrats, <@{user_id_str}> just leveled up", file = discord.File('level_up.gif'))
            with open('data.json', "w") as file:
                json.dump(data, file)

    async def on_raw_reaction_add(self,payload):
        guild_id_str = str(payload.guild_id)
        if settings[guild_id_str]["games_notifier"]:
            if payload.message_id == settings[guild_id_str]["games_notifier_message"]:
                if payload.emoji.name == "🆓":
                    guild = client.get_guild(payload.guild_id)
                    role = discord.utils.get(guild.roles, id = settings[guild_id_str]["games_notifier_role"])
                    await payload.member.add_roles(role)

    async def on_raw_reaction_remove(self,payload):
        guild_id_str = str(payload.guild_id)
        if settings[guild_id_str]["games_notifier"]:
            if payload.message_id == settings[guild_id_str]["games_notifier_message"]:
                if payload.emoji.name == "🆓":
                    guild = client.get_guild(payload.guild_id)
                    member = guild.get_member(payload.user_id)
                    role = discord.utils.get(guild.roles, id = settings[guild_id_str]["games_notifier_role"])
                    await member.remove_roles(role)
                


# bot = discord.Bot()
client = aclient()
tree = app_commands.CommandTree(client=client)

# @bot.slash_command(guild_ids=[test_guild_id])
# async def test(ctx):
#     await ctx.respond("test")

@tree.command(name="about", description="Shows about page")
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f"This is the vincent bot, created to VINCENT\n\nVersion: {version}\nGithub: https://github.com/mikeee1/vincent-bot\nReport issues: <https://github.com/mikeee1/vincent-bot/issues>", ephemeral=True)

@tree.command(name="xp", description="Shows the amount of xp you have")
async def self(interaction: discord.Interaction):
    # print(interaction.guild.id)
    # print(str(interaction.guild.id))
    # print(str(interaction.user.id))
    try:
        user_id = str(interaction.user.id)
        user_name = client.get_user(interaction.user.id)
        user_name_list = str(user_name).split("#")
        # print(user_name_list)
        guild_id = str(interaction.guild.id)
        user_avatar = interaction.user.avatar
        # print(type(interaction.user.avatar))
        file_name = f"{guild_id}.png"
        rank = calculate_rank(user_id, guild_id)
        create_xp_image(data=data, user_avatar=user_avatar, user_name_list=user_name_list, user_id=user_id, guild_id=guild_id, user_name=user_name, file_name=file_name, rank=rank)
        await interaction.response.send_message(file=discord.File(file_name))
        os.remove(file_name)
        # await interaction.response.send_message(f"<@{str(interaction.user.id)}> has {data[str(interaction.guild.id)][str(interaction.user.id)]['xp']} xp")
        # await interaction.response.send_message(f"<@{str(interaction.user.id)}> is level {data[str(interaction.guild.id)][str(interaction.user.id)]['level']}\n{data[str(interaction.guild.id)][str(interaction.user.id)]['xp']}/{level_formula_inverse(data[str(interaction.guild.id)][str(interaction.user.id)]['level']+1)} to level {data[str(interaction.guild.id)][str(interaction.user.id)]['level']+1}")
    except Exception as e:
        # print(e)
        logging.error(e)
        await interaction.response.send_message("Something went wrong", ephemeral=True)

@tree.command(name="cooldown", description="cooldown commands")
# @tree.command.default_permissions()
@app_commands.checks.has_permissions(administrator=True)
@app_commands.default_permissions(administrator=True)
@app_commands.choices(set_get = [
    Choice(name="set", value="set"),
    Choice(name="get", value="get")
])
async def self(interaction: discord.Interaction, set_get: str, amount: typing.Optional[float]):
    if set_get.lower() == "set":
        if amount != None:
            settings[str(interaction.guild.id)]['cooldown'] = amount
            with open('settings.json', "w") as file:
                json.dump(settings, file)
            # print("set")
            await interaction.response.send_message(f"The cooldown in now {settings[str(interaction.guild.id)]['cooldown']} seconds", ephemeral=True)
        else:
            await interaction.response.send_message("Please enter a amount", ephemeral=True)
    elif set_get.lower() == "get":
        # print("get")
        await interaction.response.send_message(f"The cooldown is {settings[str(interaction.guild.id)]['cooldown']} seconds", ephemeral=True)

    
    # print(interaction.guild.id)
    # print(str(interaction.guild.id))
    # print(str(interaction.user.id))
    # if not interaction
    # pass

@tree.command(name="xpget", description="Shows the amount of xp someone has")
async def self(interaction: discord.Interaction, user: discord.Member, show: typing.Optional[bool]):
    # print(user)
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
        user_id = str(user.id)
        user_name = client.get_user(user.id)
        user_name_list = str(user_name).split("#")
        # print(user_name_list)
        guild_id = str(interaction.guild.id)
        user_avatar = user.avatar
        # print(type(interaction.user.avatar))
        file_name = f"{guild_id}.png"
        rank = calculate_rank(user_id, guild_id)
        create_xp_image(data=data, user_avatar=user_avatar, user_name_list=user_name_list, user_id=user_id, guild_id=guild_id, user_name=user_name, file_name=file_name, rank=rank)
        if show:
            await interaction.response.send_message(file=discord.File(file_name))
        else:
            await interaction.response.send_message(file=discord.File(file_name), ephemeral=True)
        os.remove(file_name)
        # await interaction.response.send_message(f"{user} has {data[str(interaction.guild.id)][str(user.id)]['xp']} xp", ephemeral=True)
        # await interaction.response.send_message(f"{user} is level {data[str(interaction.guild.id)][str(user.id)]['level']}\n{data[str(interaction.guild.id)][str(user.id)]['xp']}/{level_formula_inverse(data[str(interaction.guild.id)][str(user.id)]['level']+1)} to level {data[str(interaction.guild.id)][str(user.id)]['level']+1}", ephemeral=True)
    except Exception as e:
        # print(e)
        logging.error(e)
        await interaction.response.send_message(f"Something went wrong", ephemeral=True)


@tree.command(name="scoreboard", description="Shows the scoreboard")
async def self(interaction: discord.Interaction, amount: typing.Optional[int], show: typing.Optional[bool]):
    user_id = str(interaction.user.id)
    guild_id = str(interaction.guild.id)
    folder_name = f"{guild_id}_{user_id}"
    try:
        if amount is None:
            amount = 5
        if amount <= 0:
            amount = 1
        os.mkdir(folder_name)
        data_guild = data[guild_id]
        scoreboard_list = []
        xp_list = []
        for x in data_guild.keys():
            xp_list.append(data_guild[x]["xp"])
        # xp_list = list(set(xp_list))
        xp_list.sort(reverse=True)
        xp_list = xp_list[:amount]
        # print(xp_list)
        for x in data_guild.keys():
            if data_guild[x]["xp"] in xp_list:
                scoreboard_list.append([x, data_guild[x]["xp"], calculate_rank(x, guild_id)])
        scoreboard_list.sort(key=lambda x: x[2])
        # print(scoreboard_list)
        for e, x in enumerate(scoreboard_list):
            user = client.get_user(int(x[0]))
            user_id = user.id
            user_avatar = user.avatar
            user_name = str(user)
            user_name_list = user_name.split("#")
            if user_avatar == None:
                avatar_number = int(user_name_list[1]) % 5
                avatar_url = f"https://cdn.discordapp.com/embed/avatars/{avatar_number}.png"
            else:
                avatar_url = str(user_avatar)
            avatar = requests.get(avatar_url).content
            # print(str(interaction.user.avatar).split("?")[0])
            with open(f"{folder_name}/{user_id}.png", "wb") as file:
                file.write(avatar)
            scoreboard_image_temp = Image.new(mode="RGB", size=(800, 200), color=(0,0,0,255))
            scoreboard_draw = ImageDraw.Draw(scoreboard_image_temp)
            font_big = ImageFont.truetype("arial.ttf", size=150)
            font_70 = ImageFont.truetype("arial.ttf", size=70)
            font_60 = ImageFont.truetype("arial.ttf", size=60)
            font_50 = ImageFont.truetype("arial.ttf", size=50)
            font_40 = ImageFont.truetype("arial.ttf", size=40)
            font_30 = ImageFont.truetype("arial.ttf", size=30)
            scoreboard_draw.text((50, 20), text=str(x[2]), fill="gray", font=font_big)
            scoreboard_draw.text((10, 100), text="#", fill="gray", font=font_60)
            if len(user_name) >= 18:
                if user_name[18] == " ":
                    user_name = replacer(user_name, "", 18)
                user_name = user_name[:18] + "\n" + user_name[18:]
            scoreboard_draw.text((380, 10), text=user_name, fill="gray", font=font_40)
            scoreboard_draw.text((380, 110), text=f"{x[1]} XP", fill="gray", font=font_70)
            avatar_image = Image.open(f"{folder_name}/{user_id}.png")
            avatar_image = avatar_image.resize(size=(160,160))
            scoreboard_image_temp.paste(avatar_image, (190,20))
            scoreboard_image_temp.save(f"{folder_name}/{e}.png")
            amount_of_images = e+1
        y1 = 200*amount_of_images
        scoreboard_image = Image.new(mode="RGB", size=(800, y1), color=(0,0,0,255))
        scoreboard_draw = ImageDraw.Draw(scoreboard_image)
        line_with = 5
        for x in range(amount_of_images):
            number = x + 1
            scoreboard_image_temp = Image.open(f"{folder_name}/{x}.png")
            y = 200 * x
            scoreboard_image.paste(scoreboard_image_temp, (0,y))
            # xh = 200 * number
            yh = 200 * number
            line_h = [(0, yh), (800, yh)]
            if number != amount_of_images:
                scoreboard_draw.line(line_h, fill="gray", width=line_with)
        line_v = [(160,0), (160,y1)]
        scoreboard_draw.line(line_v, fill="gray", width=line_with)
        scoreboard_image.save(f"{folder_name}/final.png")
        if show:
            await interaction.response.send_message(file=discord.File(f"{folder_name}/final.png"))
        else:
            await interaction.response.send_message(file=discord.File(f"{folder_name}/final.png"), ephemeral=True)


        shutil.rmtree(folder_name)
    except Exception as e:
        # print(e)
        logging.error(e)
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)
        await interaction.response.send_message(f"Something went wrong", ephemeral=True)


@app_commands.checks.has_permissions(administrator=True)
@app_commands.default_permissions(administrator=True)
@app_commands.choices(what_to_do = [
    Choice(name="create", value="create"),
    Choice(name="remove", value="remove")
])
@tree.command(name="games-notifier", description="Free games notifier setup")
async def self(interaction: discord.Interaction, what_to_do: str, channel: typing.Optional[discord.TextChannel], role: typing.Optional[discord.Role]):
    if what_to_do == "create":
        if channel != None and role != None:
            message = await channel.send("React with the 🆓 emoij to get notifications for free games")
            await message.pin()
            await message.add_reaction("🆓")
            guild_id_str = str(message.guild.id)
            settings[guild_id_str]["games_notifier"] = True
            settings[guild_id_str]["games_notifier_message"] = message.id
            settings[guild_id_str]["games_notifier_role"] = role.id
            settings[guild_id_str]["games_notifier_channel"] = channel.id
            with open('settings.json', "w") as file:
                json.dump(settings, file)
            await interaction.response.send_message(f"Vincent bot will now use the <#{channel.id}> channel and the <@&{role.id}> role", ephemeral=True)
    if what_to_do == "remove":
        guild_id_str = str(interaction.guild.id)
        settings[guild_id_str]["games_notifier"] = False
        with open('settings.json', "w") as file:
            json.dump(settings, file)
        await interaction.response.send_message(f"Vincent bot free game notifier has been disabled", ephemeral=True)
    # for i in data[guild_id_str].keys():
    #     data[guild_id_str][i]["games_notifier"] = False
    # with open('data.json', "w") as file:
    #     json.dump(data, file)

    # print(channel.id)
    # print(rol.id)


@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have the required permission(s)", ephemeral=True)

@tasks.loop(seconds = GAME_NOTIFIER_LOOP_SECONDS)
async def check_for_deals():
    try:
        logging.info("Checking for new free games")
        data_epic = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions")
        data_epic = json.loads(data_epic.content)
        # logging.debug(json.dumps(data_epic, indent=4))
        with open("free_games.log", "a") as file:
            file.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - {json.dumps(data_epic)}\n")
    except Exception as e:
        logging.error(e)
    else:
        try:
            data_epic = data_epic["data"]["Catalog"]["searchStore"]["elements"]
            # data_steam = requests.get("https://store.steampowered.com/search/?maxprice=free&supportedlang=english&ndl=1")
            # data_steam_soup = BeautifulSoup(data_steam.content, "html.parser")
            # test = data_steam_soup.find("div", {"id": "search_resultsRows"})
            # logging.info(test.prettify())
            
            # activity.end(datetime.fromtimestamp(time.time()+100))
            # activity.name("Time until refresh")
            if len(data_epic) > 0:
                for i in data_epic:
                    if i["promotions"] is not None:
                        if i["promotions"]["promotionalOffers"] is not None and i["price"]["totalPrice"]["discountPrice"] == 0:
                            if len(i["promotions"]["promotionalOffers"]) > 0:
                                store_name = "Epic Games"
                                store_icon_url = "https://static-00.iconduck.com/assets.00/epic-games-icon-512x512-7qpmojcd.png"
                                game_id = i["id"]
                                game_name = i["title"]
                                logging.info(game_name)
                                game_description = i["description"]
                                if game_id not in free_games["epic"]:
                                    game_end_date = i["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["endDate"]
                                    game_url = f"https://epicgames.com/store/product/{i['productSlug'] if i['productSlug'] != 'None' else i['urlSlug']}"
                                    for j in i["keyImages"]:
                                        if j["type"] == "DieselStoreFrontWide":
                                            game_thumbnail_url = j["url"]
                                            break
                                        elif j["type"] == "OfferImageWide":
                                            game_thumbnail_url = j["url"]
                                            break
                                    else:
                                        for j in i["keyImages"]:
                                            if "wide" in j["type"].lower():
                                                game_thumbnail_url = j["url"]
                                                break
                                    game_end_date_datetime = datetime.strptime(game_end_date, '%Y-%m-%dT%H:%M:%S.%fZ')
                                    game_end_date_unix = datetime.timestamp(game_end_date_datetime)
                                    game_end_date_unix += -time.timezone
                                    # print(game_end_date_unix)
                                    embed=discord.Embed(title=f"{game_name} is free on {store_name}", url=game_url, description=f"{game_description}")
                                    embed.set_author(name=f"{store_name}", icon_url=store_icon_url)
                                    embed.set_thumbnail(url=game_thumbnail_url)
                                    embed.add_field(name="Free until", value=f"<t:{int(game_end_date_unix)}>", inline=True)
                                    # await channel.send(f"")
                                    for j in settings.keys():
                                        if settings[j]["games_notifier"]:
                                            channel = client.get_channel(settings[j]["games_notifier_channel"])
                                            await channel.send(f"<@&{settings[j]['games_notifier_role']}>", embed=embed)
                                    free_games["epic"][game_id] = int(time.time())
                                    with open('free_games.json', "w") as file:
                                        json.dump(free_games, file)
            for i in list(free_games):
                for j in list(free_games[i]):
                    if free_games[i][j] + 1209600 < int(time.time()):
                        del free_games[i][j]
        except Exception as e:
            logging.error(e)
            logging.error(print(json.dumps(data_epic, sort_keys=False)))
        

client.run(TOKEN, root_logger=logger, log_handler=None)
