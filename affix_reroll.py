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


  total = sum(weighted_dict.values())


  r = random.uniform(0, total)

  upto = 0
  for key, weight in weighted_dict.items():
    if upto + weight >= r:
      return key
    upto += weight

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
    

    pool = AFFIX_REROLL["effects"].copy()

    def draw_effect(available_pool):

      weighted_effects = {effect: data["prob"] for effect, data in available_pool.items()}
      effect = weighted_random_choice(weighted_effects)

      tier_table = available_pool[effect]["tier"]

      flat_tier_prob = {}
      for tier_level, tier_values in tier_table.items():
        for val, prob in tier_values.items():
          flat_tier_prob[val] = prob

      value = weighted_random_choice(flat_tier_prob)

      return effect, value

    def format_line(effect, value):

      tiers = pool[effect]["tier"]
      tier_level_found = None
      for tier_level, tier_values in tiers.items():
        if value in tier_values:
          tier_level_found = tier_level
          break

      if tier_level_found is None:
        return f"[{effect}] {value}"

      tier_level_found = int(tier_level_found)

      if 12 <= tier_level_found <= 14:
        return f"[[{effect}] {value}](https://earth.is.gay)"
      elif tier_level_found == 15:
        return f"`[{effect}] {value}`"
      else:
        return f"[{effect}] {value}"

    def get_tier(effect, value):
      tiers = pool[effect]["tier"]
      for tier_level, tier_values in tiers.items():
        if value in tier_values:
          return tier_level
      return None


    embed = discord.Embed(title="TUNING COMPLETE")



    lines = []
    tier_list = []


    # 1. 第一行
    if random.random() < AFFIX_REROLL["first_prob"] and pool:
      effect1, value1 = draw_effect(pool)
      lines.append(format_line(effect1, value1))
      tier = get_tier(effect1, value1)
      if tier is not None:
        tier_list.append(tier)
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
      
    embed.description="\n".join(lines)
    embed.set_thumbnail(url=AFFIX_REROLL["img"])
    embed.timestamp = datetime.now(TZ_TA)
    embed.set_footer(text=str(ctx.author.display_name), icon_url=ctx.author.display_avatar.url)


    if AFFIX_IMAGE_UTILS["enable"] and AFFIX_REROLL["img_enable"]:
      file, embed = affix_image_utils(lines, tier_list, embed)
      if file:
        await ctx.send(embed=embed, file=file)
        return

    await ctx.send(embed=embed)

async def setup(bot):
  await bot.add_cog(affix_reroll_prefix(bot))
