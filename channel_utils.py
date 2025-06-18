import discord


def get_channel(guild, identifier):
  try:

    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
      return guild.get_channel(int(identifier))  
    elif isinstance(identifier, str):
      return discord.utils.get(guild.text_channels, name=identifier) 
  except Exception as e:
    print(f"get_channel {e}")
    return None
