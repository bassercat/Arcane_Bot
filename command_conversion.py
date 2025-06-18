from discord.ext.commands import CommandOnCooldown
from utils.load_json import json_data

COMMAND_CONVERSION = json_data['COMMAND_CONVERSION']
CHANNEL_IDS = json_data['CHANNEL_IDS']

COMMAND_CONVERSION['channel'] = CHANNEL_IDS[COMMAND_CONVERSION['channel']]

async def command_conversion(bot, message):
  # 忽略機器人自己或沒有頻道ID
  if message.author.bot or message.channel is None:
    return

  if not COMMAND_CONVERSION["enable"]:
    return

  # 若非目標頻道則不處理
  if message.channel.id != COMMAND_CONVERSION["channel"]:
    return

  # 取得訊息文字內容（去除前後空白）
  content = message.content.strip()
  # 將 message 包裝為 context，才能調用指令
  ctx = await bot.get_context(message)

  try:
    # 根據關鍵字轉換為對應指令（必須確保該指令已經註冊）
    if content == "抽":
      command = bot.get_command("抽")
      if command:
        await ctx.invoke(command)
      return
    elif content == "玩":
      command = bot.get_command("玩")
      if command:
        await ctx.invoke(command)
      return
    elif content == "擦":
      command = bot.get_command("擦")
      if command:
        await ctx.invoke(command)
      return
    elif content == "洗":
      command = bot.get_command("洗")
      if command:
        await ctx.invoke(command)
      return
  except CommandOnCooldown:
    # 若指令冷卻中，不顯示錯誤，只跳過
    pass

