import discord
import random
import asyncio
import time
from utils.load_json import json_data

CHAT_DRAW_ONE = json_data['CHAT_DRAW_ONE']
CHANNEL_IDS = json_data['CHANNEL_IDS']


CHAT_DRAW_ONE['channel'] = CHANNEL_IDS[CHAT_DRAW_ONE['channel']]


cooldown_temp = 0  

async def chat_draw_one(bot, message: discord.Message):
  if message.author.bot or message.channel is None:
    return

  if not CHAT_DRAW_ONE["enable"]:
    return

  if (
    message.channel.id == CHAT_DRAW_ONE["channel"]
    and "聊天室" in message.content
    and "抽一個" in message.content
  ):

    global cooldown_temp
    now = time.time()
    if now - cooldown_temp < CHAT_DRAW_ONE["cooldown"]:
      return

    cooldown_temp = now  
    channel = message.channel

    messages = [msg async for msg in channel.history(limit=50)]
    authors = set()

    for msg in messages:
      if msg.author.bot:
        continue
      authors.add(msg.author)

    if not authors:
      return

    async with message.channel.typing():
      await asyncio.sleep(8)

    chosen = random.choice(list(authors))
    await channel.send(f"幫你抽一個 抽到的是{chosen.mention}",
      reference=message,
      mention_author=True  # ping
    )
