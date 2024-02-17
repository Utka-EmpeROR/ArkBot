import asyncio
import discord
import datetime
import telebot
from discord.ext.commands import Context
from discord.ext import commands
from config import settings
from discord.ui import Button, View
from discord import ButtonStyle, InteractionType
from background import keep_alive #импорт функции для поддержки работоспособности
import os


intents = discord.Intents.default()
intents.message_content = True
Is_Active = True
Alarm = True
timer_task = None
bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)
bot2 = telebot.TeleBot(os.environ['teletoken'])

# Channel ID for the logs
LOGS_CHANNEL_ID = 1208538167742038046

# User ID to notify if both players are offline
NOTIFY_USER_ID = [410848912300310529, 466844905847783468, 403959756387254274]
# 410848912300310529 - Я
# 584808666977533953 - Кирилл
# 448120280448237569 - Ильич
# 466844905847783468 - Бука
# 449636364917407754 - Димыч
# 214377531619540992 - Олаф
# 403959756387254274 - Duke
NOTIFY_TELE_USER_ID = [1358021328]
# 1358021328 - Я
# 350506029 - Кирилл
# 772670479 - Ильич
# 848503446 - Бука
# 957622583 - Duke

@bot.event
async def on_ready():
    await bot.get_channel(LOGS_CHANNEL_ID).send("Bot just started")

@bot.command()
async def start(ctx):
    global Alarm  # Assuming Is_Active is a global variable
    Alarm = True
    await ctx.send("Alarm ON")

@bot.command()
async def stop(ctx):
    global Alarm  # Assuming Is_Active is a global variable
    Alarm = False
    await ctx.send("Alarm OFF")


async def timer_callback(duration):
    global Is_Active
    Is_Active = False
    await asyncio.sleep(duration)
    Is_Active = True
    await bot.get_channel(LOGS_CHANNEL_ID).send("Bot is Active Again")


async def stop_1_callback(interaction: discord.Interaction):
    global timer_task
    if timer_task and not timer_task.done():
        timer_task.cancel()
    await interaction.response.send_message("Muted for 1 hour")
    timer_task = asyncio.create_task(timer_callback(3600))


async def stop_4_callback(interaction: discord.Interaction):
    global timer_task
    if timer_task and not timer_task.done():
        timer_task.cancel()
    await interaction.response.send_message("Muted for 4 hour")
    timer_task = asyncio.create_task(timer_callback(14400))


@bot.command()
async def mute(ctx, duration: int = 0):
    global timer_task
    if timer_task and not timer_task.done():
        timer_task.cancel()
    if (duration == 0):
        global Is_Active
        Is_Active = False
        await ctx.send("Bot is muted")
    else:
        timer_task = asyncio.create_task(timer_callback(duration * 60))
        await ctx.send(f"Bot is muted for {duration} minutes")


@bot.command()
async def unmute(ctx):
    global timer_task
    if timer_task and not timer_task.done():
        timer_task.cancel()
    global Is_Active
    Is_Active = True
    await ctx.send("Bot is now active")



@bot.event
async def on_message(message: discord.Message):
    # Ignore messages sent by the bot
    # if message.author.bot:
    #    return
    # Check if message was sent in logs channel
    if message.channel.id != LOGS_CHANNEL_ID:
        return

    if message.content.startswith(settings['prefix']):
        # Get the command name
        command_name = message.content.split()[0][len(settings['prefix']):]

        # Check if the command exists
        if bot.get_command(command_name):
            # Process the command
            await bot.process_commands(message)
        else:
            # Command doesn't exist, delete the message
            reply = await message.reply("Invalid command")
            await message.delete()
            await asyncio.sleep(5)
            await reply.delete()
    if(Is_Active):
        if 'your tribe killed' in message.content.lower():
            if 'Valguero' in message.content and 'Megachelon' in message.content and  not "destroyed your 'C4 Charge'" in message.content :
                view = View()
                stop_1_button = Button(label="Stop for 1 hour", custom_id="stop_1")
                stop_4_button = Button(label="Stop for 4 hours", custom_id="stop_4")
                stop_1_button.callback = stop_1_callback
                stop_4_button.callback = stop_4_callback
                view.add_item(stop_1_button)
                view.add_item(stop_4_button)

                await message.reply("ALAPM", view=view)
                for id in NOTIFY_USER_ID:
                    user = await bot.fetch_user(id)
                    await user.send(message.content)
                if(Alarm):
                    for id in NOTIFY_TELE_USER_ID:
                        bot2.send_message(id, message.content)

keep_alive()  #запускаем flask-сервер в отдельном потоке.
bot.run(os.environ['discordtoken'])