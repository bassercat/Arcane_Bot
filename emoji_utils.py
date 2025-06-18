# 輸入:自訂: 轉換成<:emoji_name:emoji_id> Discord 自訂 emoji 語法（字串）
# 字串轉換，讓純文字訊息能包含表情
#使用:
#content = emoji_utils(content, channel.guild)

def emoji_text(content, guild):
    if not guild:
        return content
    for emoji in guild.emojis:
        tag = f":{emoji.name}:"
        # 會變成 <:{name}:{id}>
        code = str(emoji)  
        content = content.replace(tag, code)
    return content


#從 guild.emojis 產生名稱對應 emoji 的字典
#emoji_map = get_emoji_map(ctx.guild)
#emoji_map.get(name, name)
def get_emoji_map(guild):
  
  return {emoji.name: emoji for emoji in guild.emojis}
