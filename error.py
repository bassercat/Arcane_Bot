from discord.ext import commands


async def error(ctx, error):
  if isinstance(error, commands.CheckFailure):

    return
  elif isinstance(error, commands.CommandOnCooldown):

    return
  elif isinstance(error, commands.CommandNotFound):

    return
  else:

    raise error
