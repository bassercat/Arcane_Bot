import discord

# 工具函式：根據 identifier 取得文字頻道
# identifier 可以是頻道 ID（int 或數字字串），或頻道名稱（str）
def get_channel(guild, identifier):
  try:
    # 如果是整數，或是數字字串，嘗試當作頻道 ID 處理
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
      # 使用 ID 取得頻道
      return guild.get_channel(int(identifier))  
    # 否則如果是一般字串，當作頻道名稱處理
    elif isinstance(identifier, str):
      # 使用名稱取得頻道
      return discord.utils.get(guild.text_channels, name=identifier) 
  except Exception as e:
    print(f"get_channel {e}")
    return None