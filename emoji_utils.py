
def emoji_text(content, guild):
    if not guild:
        return content
    for emoji in guild.emojis:
        tag = f":{emoji.name}:"

        code = str(emoji)  
        content = content.replace(tag, code)
    return content



def get_emoji_map(guild):
  
  return {emoji.name: emoji for emoji in guild.emojis}
