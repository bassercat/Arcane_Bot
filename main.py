from config.env_setup import setup_env
ENV = setup_env()

import asyncio
import os
import json
import os

import discord
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown
from dotenv import load_dotenv
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv(dotenv_path="config/token.env")
if ENV == 'local':
  TOKEN = os.getenv("TOKEN_1")
elif ENV == 'colab':
  TOKEN = os.getenv("TOKEN_2")
else:
  raise SystemExit

PREFIX = os.getenv("PREFIX", "!")

from utils.load_json import load_json, json_data
from utils.error import error
from utils.channel_utils import get_channel


from config.settings import Intents

bot = commands.Bot(command_prefix=PREFIX, intents=Intents)

bot.on_command_error = error

@bot.event
async def on_message(message):
  if message.author.bot:
    return
  await bot.process_commands(message)

@bot.event
async def on_ready():
  MAIN = json_data['MAIN']


  from utils.card_image_utils import cache_card_images
  cache_card_images()

  print(f"Synced {len(bot.commands)} prefix commands")

  if MAIN["remove_global_commands"]:

    global_commands = await bot.tree.fetch_commands()
    for cmd in global_commands:
      bot.tree.remove_command(cmd.name)
    print(f"Removed {len(global_commands)} global slash & context menu commands")

    await bot.wait_until_ready()
    #await asyncio.sleep(1)
    await bot.tree.sync()

  if MAIN["sync_global_commands"]:
    synced = await bot.tree.sync()
    await bot.wait_until_ready()
    #await asyncio.sleep(1)
    print(f"Synced {len(synced)} global slash & context menu commands")

  if MAIN["remove_guild_commands"] or MAIN["sync_guild_commands"]:

    guild = discord.Object(id=MAIN['guild_id'])

    if MAIN["remove_guild_commands"]:

      guild_commands = await bot.tree.fetch_commands(guild=guild)
      for cmd in guild_commands:
        bot.tree.remove_command(cmd.name, guild=guild)
      await bot.wait_until_ready()
      #await asyncio.sleep(1)
      print(f"Removed {len(guild_commands)} guild slash & context menu commands")


    if MAIN["sync_guild_commands"]:
      synced = await bot.tree.sync(guild=guild)
      await bot.wait_until_ready()
      #await asyncio.sleep(1)
      print(f"Synced {len(synced)} guild slash & context menu commands")

  """
  print("Slash")

  slash_commands = await bot.tree.fetch_commands(guild=guild
  )
  for cmd in slash_commands:
      print(f"/{cmd.name} - {cmd.description or '（無說明）'}")

  print("Prefix")

  for cmd in bot.commands:
      print(f"!{cmd.name} - {cmd.help or '（無說明）'}")
  """

  print(f'Logged in as {bot.user}')
  print(f'------------------------------')


async def main():
  async with bot:
    load_json(ENV)


    bot.scheduler = AsyncIOScheduler()
    bot.scheduler.start()




    # prefix 指令 !s say_command
    await bot.load_extension("cogs.commands.prefix.say_command")
    # prefix 指令 !e emoji_command
    await bot.load_extension("cogs.commands.prefix.emoji_command")
    # prefix 指令 !d gacha
    await bot.load_extension("cogs.commands.prefix.gacha")
    # prefix 指令 !prob gacha_info
    await bot.load_extension("cogs.commands.prefix.gacha_info")
    # prefix 指令 !p doro_grid
    await bot.load_extension("cogs.commands.prefix.doro_grid")
    # prefix 指令 !jvc !lvc vc_join_leave
    await bot.load_extension("cogs.commands.prefix.vc_join_leave")
    # prefix 指令 !w affix_reroll
    await bot.load_extension("cogs.commands.prefix.affix_reroll")
    # prefix 指令 !c rub_doll
    await bot.load_extension("cogs.commands.prefix.rub_doll")
    # prefix 指令 !dw get_gacha_data
    await bot.load_extension("cogs.commands.prefix.get_gacha_data")
    # prefix 指令 !vcs !vcss vc_speak
    await bot.load_extension("cogs.commands.prefix.vc_speak")




    # slash 指令 /s say_command
    await bot.load_extension("cogs.commands.slash.say_command")
    # slash 指令 /e emoji_command
    await bot.load_extension("cogs.commands.slash.emoji_command")
    # slash 指令 /d gacha
    await bot.load_extension("cogs.commands.slash.gacha")
    # slash 指令 /prob gacha_info
    await bot.load_extension("cogs.commands.slash.gacha_info")
    # slash 指令 /p doro_grid
    await bot.load_extension("cogs.commands.slash.doro_grid")
    # slash 指令 /jvc /lvc vc_join_leave
    await bot.load_extension("cogs.commands.slash.vc_join_leave")
    # slash 指令 /w affix_reroll
    await bot.load_extension("cogs.commands.slash.affix_reroll")
    # slash 指令 /c rub_doll
    await bot.load_extension("cogs.commands.slash.rub_doll")
    # slash 指令 !dw get_gacha_data
    await bot.load_extension("cogs.commands.slash.get_gacha_data")
    # slash 指令 /vcs /vcss vc_speak
    await bot.load_extension("cogs.commands.slash.vc_speak")




    # context menu 指令 vertical_merge
    await bot.load_extension("cogs.commands.context_menu.vertical_merge")



    # 聊天室自動表情回應 auto emoji react
    # 指令轉換 command_conversion
    # 聊天室抽一個 chat_draw_one
    await bot.load_extension("cogs.listeners.on_message")

    # 附和反應 follow_reaction
    await bot.load_extension("cogs.listeners.follow_reaction")

    # BOT狀態
    await bot.load_extension("cogs.utils.bot_status")
    # 每日en登入
    await bot.load_extension("cogs.tasks.daily_task")



    await bot.start(TOKEN)

if __name__ == "__main__":
  asyncio.run(main())
