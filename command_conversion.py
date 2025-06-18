from discord.ext.commands import CommandOnCooldown
from utils.load_json import json_data

COMMAND_CONVERSION = json_data['COMMAND_CONVERSION']
CHANNEL_IDS = json_data['CHANNEL_IDS']

COMMAND_CONVERSION['channel'] = CHANNEL_IDS[COMMAND_CONVERSION['channel']]

async def command_conversion(bot, message):
  if message.author.bot or message.channel is None:
    return

  if not COMMAND_CONVERSION["enable"]:
    return

  if message.channel.id != COMMAND_CONVERSION["channel"]:
    return

  content = message.content.strip()
  ctx = await bot.get_context(message)

  try:
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
    pass

