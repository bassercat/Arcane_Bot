import os
import json
from discord.ext import commands
from utils.load_json import json_data

GET_GACHA_DATA = json_data['GET_GACHA_DATA']
CHANNEL_IDS = json_data['CHANNEL_IDS']

GET_GACHA_DATA['channel'] = CHANNEL_IDS[GET_GACHA_DATA['channel']]


class get_gacha_data_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="dw")
  #@commands.command(name="dw", aliases=["dw"])
  @commands.cooldown(rate=1, per=GET_GACHA_DATA["cooldown"], type=commands.BucketType.member)
  async def gacha_stats(self, ctx):

    if not GET_GACHA_DATA["enable"]:
      return
    # 判斷訊息是否來自特定允許的頻道
    if ctx.channel.id != GET_GACHA_DATA["channel"]:
      return

    

    file_path = "data/gacha_data.json"
    user_id_str = str(ctx.author.id)

    if not os.path.exists(file_path):
      return

    with open(file_path, "r", encoding="utf-8") as f:
      data = json.load(f)

    if user_id_str not in data:
      return

    user_data = data[user_id_str]

    msg = (
      f"{ctx.author.display_name}\n"
      f"總抽卡次數：{user_data['total']} 次\n"
      f"R 卡數量：{user_data['r']} 張\n"
      f"SR 卡數量：{user_data['sr']} 張\n"
      f"SSR 卡數量：{user_data['ssr']} 張\n"
      f"--- SSR 詳細 ---\n"
    )

    if user_data["ssr_detail"]:
      sorted_ssr = sorted(user_data["ssr_detail"].items(), key=lambda x: x[1], reverse=True)
      for name, count in sorted_ssr:
        msg += f"{name}：{count} 張\n"
    else:
      msg += "目前沒有 SSR 詳細資料。"

    await ctx.author.send(msg)


    
# 註冊 COG
async def setup(bot):
  await bot.add_cog(get_gacha_data_prefix(bot))