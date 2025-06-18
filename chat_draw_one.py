import discord
import random
import asyncio
import time
from utils.load_json import json_data

CHAT_DRAW_ONE = json_data['CHAT_DRAW_ONE']
CHANNEL_IDS = json_data['CHANNEL_IDS']


CHAT_DRAW_ONE['channel'] = CHANNEL_IDS[CHAT_DRAW_ONE['channel']]


# 冷卻秒數
cooldown_temp = 0  

async def chat_draw_one(bot, message: discord.Message):
  # 忽略機器人自己或沒有頻道ID
  if message.author.bot or message.channel is None:
    return

  if not CHAT_DRAW_ONE["enable"]:
    return

  # 判斷是否在目標頻道，且訊息中包含「抽一個」
  if (
    message.channel.id == CHAT_DRAW_ONE["channel"]
    and "聊天室" in message.content
    and "抽一個" in message.content
  ):

    global cooldown_temp
    now = time.time()
    # 判斷是否冷卻中
    if now - cooldown_temp < CHAT_DRAW_ONE["cooldown"]:
      return

    # 更新冷卻時間
    cooldown_temp = now  
    channel = message.channel

    # 取得最近50條訊息（排除bot訊息）
    messages = [msg async for msg in channel.history(limit=50)]
    # 使用 set 避免重複作者
    authors = set()

    for msg in messages:
      # 跳過機器人訊息
      if msg.author.bot:
        continue
      authors.add(msg.author)

    # 如果沒有找到任何作者，就不執行
    if not authors:
      return

    # 顯示打字中...
    async with message.channel.typing():
      await asyncio.sleep(8)

    chosen = random.choice(list(authors))
    await channel.send(f"幫你抽一個 抽到的是{chosen.mention}",
      reference=message,
      mention_author=True  # ping
    )
