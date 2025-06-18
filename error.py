from discord.ext import commands

# 靜默處理沒有權限 冷卻中 錯誤

async def error(ctx, error):
  if isinstance(error, commands.CheckFailure):
    # 沒權限就不回應任何訊息
    return
  elif isinstance(error, commands.CommandOnCooldown):
    # 冷卻中也不回應任何訊息
    return
  elif isinstance(error, commands.CommandNotFound):
    # 靜默忽略指令不存在的錯誤，不輸出任何訊息
    return
  else:
    # 其餘錯誤仍拋出（方便除錯）
    raise error