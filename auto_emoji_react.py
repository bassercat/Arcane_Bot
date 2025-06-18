import random
import asyncio
from utils.emoji_utils import emoji_text
from utils.load_json import json_data

AUTO_EMOJI_REACT = json_data['AUTO_EMOJI_REACT']
CHANNEL_IDS = json_data['CHANNEL_IDS']


AUTO_EMOJI_REACT['channel'] = CHANNEL_IDS[AUTO_EMOJI_REACT['channel']]

async def auto_emoji_react(bot, message):
  
  if message.author.bot or message.channel is None:
    return

  if (
    message.channel.id == AUTO_EMOJI_REACT["channel"] 
    and AUTO_EMOJI_REACT["enable"]
  ):

    if random.random() < AUTO_EMOJI_REACT["prob"]:  
        

      async with message.channel.typing():
        await asyncio.sleep(8)

      chosen_name = random.choice(AUTO_EMOJI_REACT["emojis"])
      emoji_code = emoji_text(f":{chosen_name}:", message.guild)
      emoji_to_use = emoji_code if emoji_code != f":{chosen_name}:" else chosen_name

      already_reacted = False
      for reaction in message.reactions:
        if str(reaction.emoji) == emoji_to_use:
          async for user in reaction.users():
            if user == bot.user:
              already_reacted = True
              break
        if already_reacted:
          break

      if not already_reacted:
        try:
          await message.add_reaction(emoji_to_use)
        except Exception:
          pass
