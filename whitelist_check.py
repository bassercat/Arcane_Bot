from discord.ext import commands
from utils.load_json import json_data


def is_whitelisted():
    async def predicate(ctx):
      WHITE_LIST_IDS = json_data['WHITE_LIST_IDS']  
      return ctx.author.id in WHITE_LIST_IDS
    return commands.check(predicate)
