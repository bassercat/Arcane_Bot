from discord.ext import commands
import discord
from utils.load_json import json_data
import time

FOLLOW_REACTION = json_data['FOLLOW_REACTION']
CHANNEL_IDS = json_data['CHANNEL_IDS']

FOLLOW_REACTION['channel'] = CHANNEL_IDS[FOLLOW_REACTION['channel']]

class follow_reaction(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.last_react_time = 0  
    self.cooldown = FOLLOW_REACTION['cooldown']

  @commands.Cog.listener()
  async def on_reaction_add(self, reaction, user):

    if user.bot:
      return

    if not FOLLOW_REACTION["enable"]:
      return

    message = reaction.message

    if message.channel.id != FOLLOW_REACTION["channel"]:
      return

    now = time.time()
    if now - self.last_react_time < self.cooldown:
      return
    self.last_react_time = now


    if reaction.count >= 3:
      message = reaction.message
      emoji = reaction.emoji

      for r in message.reactions:
        if r.emoji == emoji and r.me:
          return  

      try:
        await message.add_reaction(emoji)
      except discord.HTTPException:
        print(f"follow_reaction error {emoji}")


async def setup(bot):
    await bot.add_cog(follow_reaction(bot))
