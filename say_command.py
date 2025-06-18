from discord.ext import commands
from utils.channel_utils import get_channel
from utils.load_json import json_data

SAY_COMMAND = json_data['SAY_COMMAND']
CHANNEL_IDS = json_data['CHANNEL_IDS']

SAY_COMMAND['channel'] = CHANNEL_IDS[SAY_COMMAND['channel']]
SAY_COMMAND['command'] = CHANNEL_IDS[SAY_COMMAND['command']]

class say_command_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # 指令：s
  @commands.command(name="s")
  async def s(self, ctx, *args):
    if not SAY_COMMAND["enable"]:
      return

    # 不在允許頻道，沒打字 不做任何回應
    if ctx.channel.id != SAY_COMMAND["command"] or not args:
      return
    
    # 找出對應伺服器要發送的頻道ID
    target_channel = get_channel(ctx.guild, SAY_COMMAND["channel"])
    if not target_channel:
      return
    # 回覆的訊息 ID，預設為 None
    message_id = None
    # 訊息內容從第幾個參數開始
    content_start_index = 0

    # 嘗試判斷第一個參數是頻道ID或名稱，或訊息ID（回覆用）
    # 用 get_channel 取得目標頻道，失敗回傳None表示第一參數不是頻道
    # 第一個參數是頻道ID或名稱，切換目標頻道
    temp_channel = get_channel(ctx.guild, args[0])
    if temp_channel:
      target_channel = temp_channel
      content_start_index = 1

      # 第二個參數如果存在，且是數字且長度大於等於10，視為訊息ID（回覆用）
      if len(args) > 1 and args[1].isdigit() and len(args[1]) >= 10:
        try:
          test_message = await target_channel.fetch_message(int(args[1]))
          message_id = int(args[1])
          content_start_index = 2
        except:
          message_id = None
          content_start_index = 1
    # 第一參數不是頻道，判斷是否為訊息ID（回覆預設頻道的訊息）
    elif args[0].isdigit() and len(args[0]) >= 10:
      try:
        test_message = await target_channel.fetch_message(int(args[0]))
        message_id = int(args[0])
        content_start_index = 1
      except:
        message_id = None
        content_start_index = 0


    # 組合後續參數作為要發送的訊息內容
    content = ' '.join(args[content_start_index:]).strip()
    if not content and not ctx.message.attachments:
      # 沒訊息就不執行
      return

    try:
      # 處理附件（圖片）
      files = []
      if ctx.message.attachments:
        for attachment in ctx.message.attachments:
          file = await attachment.to_file()
          files.append(file)

      if message_id:
        # 有訊息ID，視為回覆，嘗試取得該訊息
        sent_message = await target_channel.send(content or None, reference=test_message, files=files)
      else:
        # 沒有訊息ID
        sent_message = await target_channel.send(content or None, files=files)
      
      # 建立訊息連結
      msg_link = f"https://discord.com/channels/{ctx.guild.id}/{target_channel.id}/{sent_message.id}"
      # 回覆指令使用者
      await ctx.send(f"{msg_link}")

    except Exception as e:
      # 抓不到訊息或錯誤時
      print(f"say_command error {e}")
      
# COG 載入函式
async def setup(bot):
  await bot.add_cog(say_command_prefix(bot))