import discord
from discord.ext import commands
from datetime import datetime
import random
from utils.load_json import json_data
from config.settings import TZ_TA
from utils.affix_image_utils import affix_image_utils


AFFIX_REROLL = json_data['AFFIX_REROLL']
CHANNEL_IDS = json_data['CHANNEL_IDS']
AFFIX_IMAGE_UTILS = json_data['AFFIX_IMAGE_UTILS']

AFFIX_REROLL['channel'] = CHANNEL_IDS[AFFIX_REROLL['channel']]

def weighted_random_choice(weighted_dict):

  # 計算所有權重的總和
  total = sum(weighted_dict.values())

  # 在 0 到 total 之間生成一個隨機浮點數 r
  r = random.uniform(0, total)

  upto = 0
  # 逐個遍歷字典的項目 (key, weight)
  for key, weight in weighted_dict.items():
    # 判斷如果加上這個權重後，是否超過了隨機數 r
    if upto + weight >= r:
      # 如果是，回傳這個 key，代表抽中了它
      return key
    # 否則把目前的權重累加到 upto，繼續下一個 key 的判斷
    upto += weight

  # 正常情況不會走到這裡（因為會提前 return），
  # 但如果有浮點數誤差，就回傳最後一個 key 防呆
  return list(weighted_dict.keys())[-1]

class affix_reroll_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="w", aliases=["洗"])
  @commands.cooldown(rate=1, per=AFFIX_REROLL["cooldown"], type=commands.BucketType.member)
  async def random_entries(self, ctx):

    if not AFFIX_REROLL["enable"]:
      return

    if ctx.channel.id != AFFIX_REROLL["channel"]:
      return
    

    # 複製 main_prob，避免後續 pop 影響原資料
    pool = AFFIX_REROLL["effects"].copy()

    def draw_effect(available_pool):

      # 建立一個新字典 key是effect value是prob 做權重抽選
      weighted_effects = {effect: data["prob"] for effect, data in available_pool.items()}
      effect = weighted_random_choice(weighted_effects)

      # tier 是字典型態：{tier_level: {value: prob, ...}, ...}
      tier_table = available_pool[effect]["tier"]

      # 將所有 tier_level 下的數值與機率攤平成一個 dict {value: prob}
      flat_tier_prob = {}
      for tier_level, tier_values in tier_table.items():
        for val, prob in tier_values.items():
          flat_tier_prob[val] = prob

      # 從攤平後的數值機率中抽一個數值
      value = weighted_random_choice(flat_tier_prob)

      return effect, value

    def format_line(effect, value):

      tiers = pool[effect]["tier"]
      tier_level_found = None
      # 找出 value 對應的 tier_level
      for tier_level, tier_values in tiers.items():
        if value in tier_values:
          tier_level_found = tier_level
          break

      if tier_level_found is None:
        # 找不到對應 tier，回傳普通格式
        return f"[{effect}] {value}"

      tier_level_found = int(tier_level_found)

      if 12 <= tier_level_found <= 14:
        # 12~14 tier 以 [] 括號，並加個連結示意（示意用 URL）
        return f"[[{effect}] {value}](https://earth.is.gay)"
      elif tier_level_found == 15:
        # tier 15 以反引號包覆
        return f"`[{effect}] {value}`"
      else:
        return f"[{effect}] {value}"

    def get_tier(effect, value):
      tiers = pool[effect]["tier"]
      for tier_level, tier_values in tiers.items():
        if value in tier_values:
          return tier_level
      return None


    # 建立嵌入訊息
    embed = discord.Embed(title="TUNING COMPLETE")


    # 開始抽卡流程
    lines = []
    tier_list = []


    # 1. 第一行
    if random.random() < AFFIX_REROLL["first_prob"] and pool:
      effect1, value1 = draw_effect(pool)
      lines.append(format_line(effect1, value1))
      tier = get_tier(effect1, value1)
      if tier is not None:
        tier_list.append(tier)
      # 抽過的效果移除避免重複
      pool.pop(effect1)  
    else:
      tier_list.append(-1)
      lines.append("未獲得效果")

    # 2. 第二行
    if random.random() < AFFIX_REROLL["second_prob"] and pool:
      effect2, value2 = draw_effect(pool)
      lines.append(format_line(effect2, value2))
      tier = get_tier(effect2, value2)
      if tier is not None:
        tier_list.append(tier)
      pool.pop(effect2)
    else:
      tier_list.append(-1)
      lines.append("未獲得效果")

    # 3. 第三行
    if random.random() < AFFIX_REROLL["third_prob"] and pool:
      effect3, value3 = draw_effect(pool)
      lines.append(format_line(effect3, value3))
      tier = get_tier(effect3, value3)
      if tier is not None:
        tier_list.append(tier)
    else:
      tier_list.append(-1)
      lines.append("未獲得效果")


    tier_line = "`" + ", ".join(
      "  " if tier == -1 else f"T{tier}"
      for tier in tier_list
    ) + "`"

    lines.append("")
    lines.append(tier_line)
    embed.description = "\n".join(lines)
    
    max_tier = max((int(x) for x in tier_list), default=0)

    if max_tier >= 15:
      embed.color = discord.Color.from_rgb(0, 0, 0)
    elif max_tier >= 12:
      embed.color = discord.Color.blue()
    else:
      pass

    # 把 lines 這個字串串列合成一個用換行符號分隔的字串
    embed.description="\n".join(lines)
    # 設定縮圖
    embed.set_thumbnail(url=AFFIX_REROLL["img"])
    # 設定時間戳記，方便紀錄
    embed.timestamp = datetime.now(TZ_TA)
    # 設定頁尾顯示使用者名稱與大頭貼
    embed.set_footer(text=str(ctx.author.display_name), icon_url=ctx.author.display_avatar.url)


    if AFFIX_IMAGE_UTILS["enable"] and AFFIX_REROLL["img_enable"]:
      file, embed = affix_image_utils(lines, tier_list, embed)
      if file:
        await ctx.send(embed=embed, file=file)
        return

    # 傳送結果
    await ctx.send(embed=embed)

async def setup(bot):
  await bot.add_cog(affix_reroll_prefix(bot))