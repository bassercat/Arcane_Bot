import discord
import random
from datetime import datetime
from collections import Counter
from discord.ext import commands
from utils.card_image_utils import compose_cards
from utils.load_json import json_data
from config.settings import TZ_TA 
import json
import os

GACHA = json_data['GACHA']
CARD_IMAGE_UTILS = json_data['CARD_IMAGE_UTILS']
CHANNEL_IDS = json_data['CHANNEL_IDS']

GACHA['channel'] = CHANNEL_IDS[GACHA['channel']]

def save_gacha_data(
  user_id: int, results: list, count_R: int,
  count_SR: int, ssr_cards: list,
  file_path=GACHA['gacha_data_path'],
  backup_file_path=GACHA.get('gacha_data_backup_path')
  ):


  user_id_str = str(user_id)


  if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
      data = json.load(f)
  else:
    data = {}


  if user_id_str not in data:
    data[user_id_str] = {
      "total": 0,
      "r": 0,
      "sr": 0,
      "ssr": 0,
      "ssr_detail": {}
    }


  data[user_id_str]["total"] += len(results)
  data[user_id_str]["r"] += count_R
  data[user_id_str]["sr"] += count_SR
  data[user_id_str]["ssr"] += len(ssr_cards)


  for ssr_name in ssr_cards:
      if ssr_name not in data[user_id_str]["ssr_detail"]:
          data[user_id_str]["ssr_detail"][ssr_name] = 0
      data[user_id_str]["ssr_detail"][ssr_name] += 1


  os.makedirs(os.path.dirname(file_path), exist_ok=True)
  with open(file_path, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)

  if backup_file_path:
    os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
    with open(backup_file_path, "w", encoding="utf-8") as f_backup:
      json.dump(data, f_backup, ensure_ascii=False, indent=2)




class gacha_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  def draw_one_card(self):

    r = random.random()

    if r < GACHA["r_prob"]:
      name = random.choice(GACHA['pool']['r'])
      return "R", name

    elif r < GACHA["r_prob"] + GACHA["sr_prob"]:
      name = random.choice(GACHA['pool']['sr'])
      return "SR", name 
    else:

      r2 = random.random()
 
      if r2 < GACHA["ssr_pickup_prob"] / GACHA["ssr_prob"]:
        name = random.choice(GACHA['pool']['ssr_pickup'])
        return f"SSR (PICKUP) {name}", name

      elif r2 < (GACHA["ssr_pickup_prob"] + GACHA["ssr_pilgrims_prob"]) / GACHA["ssr_prob"]:
        name = random.choice(GACHA['pool']['ssr_pilgrims'])
        return f"SSR (Pilgrims) {name}", name
      else:
        name = random.choice(GACHA['pool']['ssr_others'])  
        return f"SSR (Others) {name}", name



  @commands.command(name="d", aliases=["抽"])
  @commands.cooldown(rate=1, per=GACHA["cooldown"], type=commands.BucketType.member)
  async def d(self, ctx):
    
    if not GACHA["enable"]:
      return

    if ctx.channel.id != GACHA["channel"]:
      return


    results = [self.draw_one_card() for _ in range(GACHA["max_gacha"])]


    count_R = sum(1 for text, _ in results if text == "R")
    count_SR = sum(1 for text, _ in results if text == "SR")
    ssr_cards = [img_name for text, img_name in results if text.startswith("SSR")]
    ssr_counter = Counter(ssr_cards)

    lines=[]

    if count_R != 0:
      lines.append(f"R 共{count_R}隻\n")
    if count_SR != 0:
      lines.append(f"SR 共{count_SR}隻\n")



    for pickup_name in GACHA['pool']["ssr_pickup"]:
      if pickup_name in ssr_counter:
        lines.append(f"{pickup_name} 共{ssr_counter[pickup_name]}隻\n")
        del ssr_counter[pickup_name]

    for name in sorted(ssr_counter):
      lines.append(f"{name} 共{ssr_counter[name]}隻\n")
    


    lines.append("\n")
    cleaned_results = [
      text.split()[-1] if text.startswith("SSR") else text
      for text, _ in results
    ]
    spoiler_line = f"||{', '.join(cleaned_results)}||"
    lines.append(spoiler_line)



    embed = discord.Embed(
      title=f"{GACHA['max_gacha']}抽結果",
      description="".join(lines),

      color=discord.Color.gold(),
      timestamp=datetime.now(TZ_TA)
    )
    
    embed.set_footer(text=str(ctx.author.display_name), icon_url=ctx.author.display_avatar.url)
 

    if ssr_counter or any(pickup_name in line for line in lines):
      embed.set_thumbnail(url=GACHA["ssr_img"])
      embed.color=discord.Color.from_rgb(*GACHA["ssr_embed_color"])
    elif count_SR != 0:
      embed.set_thumbnail(url=GACHA["sr_img"])
      embed.color=discord.Color.from_rgb(*GACHA["sr_embed_color"])
    elif count_R != 0:
      embed.set_thumbnail(url=GACHA["r_img"])
      embed.color=discord.Color.from_rgb(*GACHA["r_embed_color"])

    if GACHA["save_enable"]:
      save_gacha_data(
          user_id=ctx.author.id,
          results=results,
          count_R=count_R,
          count_SR=count_SR,
          ssr_cards=ssr_cards
      )


    if CARD_IMAGE_UTILS["enable"] and GACHA["img_enable"]:
      file, embed = await compose_cards(results, embed)
      if file:
        await ctx.send(embed=embed, file=file)
        return
    
    await ctx.send(embed=embed)







async def setup(bot):
  await bot.add_cog(gacha_prefix(bot))
