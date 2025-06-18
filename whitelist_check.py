from discord.ext import commands
from utils.load_json import json_data

#回傳一個裝飾器，用於檢查使用者是否在白名單中

def is_whitelisted():
    async def predicate(ctx):
      WHITE_LIST_IDS = json_data['WHITE_LIST_IDS']  
      return ctx.author.id in WHITE_LIST_IDS
    return commands.check(predicate)