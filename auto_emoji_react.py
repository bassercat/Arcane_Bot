import random
import asyncio
from utils.emoji_utils import emoji_text
from utils.load_json import json_data

AUTO_EMOJI_REACT = json_data['AUTO_EMOJI_REACT']
CHANNEL_IDS = json_data['CHANNEL_IDS']


AUTO_EMOJI_REACT['channel'] = CHANNEL_IDS[AUTO_EMOJI_REACT['channel']]

async def auto_emoji_react(bot, message):
  # 忽略機器人自己或沒有頻道ID
  if message.author.bot or message.channel is None:
    return

  # 不在允許頻道，沒打字 不做任何回應
  if (
    message.channel.id == AUTO_EMOJI_REACT["channel"] 
    and AUTO_EMOJI_REACT["enable"]
  ):
    # 機率反應
    if random.random() < AUTO_EMOJI_REACT["prob"]:  
        
      # 顯示打字中...
      async with message.channel.typing():
        await asyncio.sleep(8)

      # 隨機選擇一個 emoji 名稱
      chosen_name = random.choice(AUTO_EMOJI_REACT["emojis"])
      # 使用工具函式將 :name: 轉換為 <:name:id> 語法
      emoji_code = emoji_text(f":{chosen_name}:", message.guild)
      # 判斷轉換後是否成功
      emoji_to_use = emoji_code if emoji_code != f":{chosen_name}:" else chosen_name

      # 檢查是否已經加過這個 emoji
      already_reacted = False
      for reaction in message.reactions:
        if str(reaction.emoji) == emoji_to_use:
          async for user in reaction.users():
            if user == bot.user:
              already_reacted = True
              break
        if already_reacted:
          break

      # 加反應（如果尚未加過）
      if not already_reacted:
        try:
          await message.add_reaction(emoji_to_use)
        except Exception:
          pass
