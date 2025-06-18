import discord
from discord.ext import commands
from utils.channel_utils import get_channel
from utils.load_json import json_data
EMOJI_COMMAND = json_data['EMOJI_COMMAND']
CHANNEL_IDS = json_data['CHANNEL_IDS']

EMOJI_COMMAND['channel'] = CHANNEL_IDS[EMOJI_COMMAND['channel']]
EMOJI_COMMAND['command'] = CHANNEL_IDS[EMOJI_COMMAND['command']]

class emoji_command_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # 指令：!e
  @commands.command(name='e')
  async def e(self, ctx, *args):
    if not EMOJI_COMMAND["enable"]:
      return

    # 不在允許頻道，沒打字 不做任何回應
    if ctx.channel.id != EMOJI_COMMAND["command"] or len(args) < 2:
      return

    # 找出對應伺服器要發送的頻道ID
    target_channel = get_channel(ctx.guild, EMOJI_COMMAND["channel"])
    if not target_channel:
      return


    # 嘗試判斷第一個參數是頻道ID或名稱，或訊息ID（回覆用）
    # 用 get_channel 取得目標頻道，失敗回傳None表示第一參數不是頻道
    # 第一個參數是頻道ID或名稱，切換目標頻道
    temp_channel = get_channel(ctx.guild, args[0])
    if temp_channel:
      target_channel = temp_channel      

      # 第二個參數如果存在，且是數字且長度大於等於10，視為訊息ID（回覆用）
      if len(args) > 1 and args[1].isdigit() and len(args[1]) >= 10:
        try:
          target_message = await target_channel.fetch_message(int(args[1]))
          message_id = int(args[1])
          emoji_index = 2
        except:
          #抓不到訊息ID跳出
          return

    # 第一參數不是頻道，判斷是否為訊息ID（回覆預設頻道的訊息）
    elif args[0].isdigit() and len(args[0]) >= 10:
      try:
        target_message = await target_channel.fetch_message(int(args[0]))
        message_id = int(args[0])
        emoji_index = 1
      except:
        #抓不到訊息ID跳出
        return
    else:
      # 第一參數既不是頻道也不是訊息ID，就不處理
      return

    if not target_message:
      return


    emojis = args[emoji_index:]
    
    try:
      # 建立已反應過的 emoji 集合
      reacted_emojis = set()

      # 從訊息中檢查機器人是否已反應過哪些 emoji
      for reaction in target_message.reactions:
        async for user in reaction.users():
          if user == self.bot.user:
            reacted_emojis.add(str(reaction.emoji))
            break  # 一個人就夠

      # 對每個 emoji 順序處理（若已有反應則移除，否則加上）
      for emoji_raw in emojis:
        try:
          if emoji_raw in reacted_emojis:
            await target_message.remove_reaction(emoji_raw, self.bot.user)
            reacted_emojis.remove(emoji_raw)
          else:
            await target_message.add_reaction(emoji_raw)
            reacted_emojis.add(emoji_raw)

        except discord.errors.HTTPException as e:
          # emoji 格式錯誤（例如打了不存在的 custom emoji）
          if "Unknown Emoji" in e.text:
            pass
          else:
            print(f"emoji_command error {e}")
        except Exception as e:
          print(f"emoji_command error {e}")

      # 建立訊息連結
      msg_link = f"https://discord.com/channels/{ctx.guild.id}/{target_channel.id}/{target_message.id}"
      # 回覆指令使用者
      await ctx.send(f"{msg_link}")

    except Exception as e:
      print(f"emoji_command error {e}")


# Cog 載入用
async def setup(bot):
  await bot.add_cog(emoji_command_prefix(bot))
