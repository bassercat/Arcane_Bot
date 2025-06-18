import discord
from discord.ext import commands
from utils.load_json import json_data
import hashlib
from pathlib import Path

BOT_STATUS = json_data['BOT_STATUS']
MAIN = json_data['MAIN']



async def get_avatar_bytes(asset: discord.Asset):
    return await asset.read()

def hash_bytes(data: bytes):
    return hashlib.sha256(data).hexdigest()



class bot_status(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.avatar_hash = None

  @commands.Cog.listener()
  async def on_ready(self):

    now_set = {}
    set_ = BOT_STATUS['current']
    now_set = BOT_STATUS[set_]
    guild = self.bot.get_guild(MAIN['guild_id'])

    with open(now_set['avatar'], "rb") as f:
      avatar_bytes = f.read()
    target_hash = hash_bytes(avatar_bytes)

    current_hash = None

    if self.bot.user.avatar:  
      current_bytes = await self.bot.user.avatar.read()
      current_hash = hash_bytes(current_bytes)

    if current_hash != target_hash:
      try:
        path = Path(now_set['avatar'])
        await self.bot.user.edit(avatar=avatar_bytes)
        print(f"Avatar change {path.name}")
      except Exception as e:
        print(f"bot_status error {e}")



    try:
      if guild is not None:
        me = guild.me
        target_nick = now_set.get("name", "BOT")
        if me.nick != target_nick:
          await me.edit(nick=target_nick)
          print(f"Nickname change {target_nick}")
    except Exception as e:
        print(f"bot_status error {e}")



    activity = discord.CustomActivity(name=now_set["activity"])



    status = now_set.get("status", "online")
    # 字串合併屬性
    status_enum = getattr(discord.Status, status)
    await self.bot.change_presence(status=status_enum, activity=activity)
    


async def setup(bot: commands.Bot):
  await bot.add_cog(bot_status(bot))
