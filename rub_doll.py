import discord
from discord.ext import commands
import random
from datetime import datetime
from utils.load_json import json_data
from config.settings import TZ_TA 

RUB_DOLL = json_data['RUB_DOLL']
CHANNEL_IDS = json_data['CHANNEL_IDS']

RUB_DOLL['channel'] = CHANNEL_IDS[RUB_DOLL['channel']]



player_data = {}




def get_bar(exp, max_exp=3000, length=15):
  filled_len = int(exp / max_exp * length)
  empty_len = length - filled_len
  bar = "█" * filled_len + "░" * empty_len
  return f"[{bar}]"



def get_feed_prob(level, doll, feed_type):
  if level >= RUB_DOLL["max_level"]:
    return 0.0
  idx = level * 3
  type_idx = {'r': 0, 'sr': 1, 'ssr': 2}[feed_type]
  prob_table = {
    'r': RUB_DOLL["r_crit_prob"],
    'sr': RUB_DOLL["sr_crit_prob"],
  }
  return prob_table[doll][idx + type_idx]



def get_star_img(level, doll):
  if level < 5:
    star = "☆☆☆"
    img = RUB_DOLL[f"{doll}_0_img"]
  elif level <10:
    star = "★☆☆"
    img = RUB_DOLL[f"{doll}_5_img"]
  elif level < 15:
    star = "★★☆"
    img = RUB_DOLL[f"{doll}_10_img"]
  else:
    star = "★★★"
    img = RUB_DOLL[f"{doll}_15_img"]
  return star, img



class rub_doll_view(discord.ui.View):
  def __init__(self, user_id, player_data):
    super().__init__(timeout=RUB_DOLL["view_timeout"])
    self.user_id = user_id
    self.player_data = player_data
    self.r_sr_on = True
    self.message = None

    true_or_false = self.player_data['level'] >= RUB_DOLL["max_level"]
    
    level = self.player_data['level']
    if level >= RUB_DOLL["max_level"]:
      r_feed_prob = sr_feed_prob = ssr_feed_prob = "-"
    else:
      r_feed_prob =  f"{round(get_feed_prob(level, self.player_data.get('doll', 'r'), 'r') * 100, 1)}"
      sr_feed_prob =  f"{round(get_feed_prob(level, self.player_data.get('doll', 'r'), 'sr') * 100, 1)}"
      ssr_feed_prob =  f"{round(get_feed_prob(level, self.player_data.get('doll', 'r'), 'ssr') * 100, 1)}"

    self.r_feed_button = rub_doll_button(f"R {r_feed_prob}%", "r", self, disabled=true_or_false)
    self.sr_feed_button = rub_doll_button(f"SR {sr_feed_prob}%", "sr", self, disabled=true_or_false)
    self.ssr_feed_button = rub_doll_button(f"SSR {ssr_feed_prob}%", "ssr", self, disabled=true_or_false)
    self.start_doll_button = rub_doll_button2(self)
    self.r_to_sr_button = rub_doll_button3(self)

    self.add_item(self.r_feed_button)
    self.add_item(self.sr_feed_button)
    self.add_item(self.ssr_feed_button)

    if self.r_sr_on:
      self.add_item(self.start_doll_button)

    
  async def on_timeout(self):
    for child in self.children:
      if isinstance(child, discord.ui.Button):
        child.disabled = True


class rub_doll_button(discord.ui.Button):
  def __init__(self, label, feed_type, view_, disabled=False):

    super().__init__(label=label, disabled=disabled)
    self.feed_type = feed_type
    self.user_id = view_.user_id

  async def callback(self, interaction: discord.Interaction):
    
    if interaction.user.id != self.user_id or self.view.player_data['level'] >= RUB_DOLL["max_level"]:
      await interaction.response.defer(ephemeral=True)
      return

    self.view.r_sr_on = False 

    for child in self.view.children:
      if isinstance(child, rub_doll_button2):
        self.view.remove_item(child)
        break

    await handle_feed(self.view, interaction, self.feed_type)


async def handle_feed(view, interaction, feed_type):


  view.player_data["last_success"] = False


  for child in view.children:
    if isinstance(child, discord.ui.Button):
      child.disabled = True


  view.player_data['used'][feed_type] += 1

  crit_prob = get_feed_prob(view.player_data['level'], view.player_data['doll'], feed_type)


  if random.random() < crit_prob:
    view.player_data["last_success"] = True
    if view.player_data['level'] < 5:
      view.player_data['level'] = 5
      view.player_data['exp'] = 0
    elif view.player_data['level'] < 10:
      view.player_data['level'] = 10
      view.player_data['exp'] = 0
    elif view.player_data['level'] < 15:
      view.player_data['level'] = 15
      view.player_data['exp'] = 3000
  else:

    view.player_data['exp'] += RUB_DOLL["feed_exp"][feed_type]


    while (
      view.player_data['exp'] >= RUB_DOLL["level_up_exp"] and
      view.player_data['level'] < RUB_DOLL["max_level"]
    ):
      view.player_data['level'] += 1

      if view.player_data['level'] in (5, 10):
        view.player_data['exp'] = 0
      elif view.player_data['level'] == 15:
        view.player_data['exp'] = 3000
      else:

        view.player_data['exp'] -= RUB_DOLL["level_up_exp"]


  await update_message(view, interaction)



async def update_message(view, interaction):
  

  level = view.player_data['level']
  exp = view.player_data['exp']
  used = view.player_data['used']
  start_time = view.player_data['start_time']
  doll = view.player_data['doll']

  embed = discord.Embed(title=f"擦娃娃 {doll.upper()}")
  
  if start_time:
    embed.set_footer(
      text=interaction.user.display_name,
      icon_url=interaction.user.display_avatar.url
    )
    embed.timestamp = start_time
  
  star, img = get_star_img(level, doll)
  bar = get_bar(exp)
  embed.set_thumbnail(url=img)


  if view.player_data.get("last_success"):
    add = " ✨"
  else:
    add = ""

  if level < RUB_DOLL["max_level"]:
    level_text = star+" "+str(level)+"階級"+add

    exp_text = str(exp)+"/3000"    
    
  else:
    level_text = star+" "+str(RUB_DOLL['max_level'])+"階級"+add

    exp_text = "MAX"

  used_text = (
    " ".join([f"{k.upper()}:{v * 10}個"
    for k, v in view.player_data['used'].items()])
  
  )

  embed.description = (
    level_text+"\n"+
    exp_text+"\n"+
    bar+"\n"+
    "總用數\n"+
    used_text
  )


  if level >= RUB_DOLL["max_level"]:
    r_feed_prob = sr_feed_prob = ssr_feed_prob = "-"
  else:
    r_feed_prob =  f"{round(get_feed_prob(level, view.player_data.get('doll', 'r'), 'r') * 100, 1)}"
    sr_feed_prob =  f"{round(get_feed_prob(level, view.player_data.get('doll', 'r'), 'sr') * 100, 1)}"
    ssr_feed_prob =  f"{round(get_feed_prob(level, view.player_data.get('doll', 'r'), 'ssr') * 100, 1)}"

  view.r_feed_button.label = f"R {r_feed_prob}%"
  view.sr_feed_button.label = f"SR {sr_feed_prob}%"
  view.ssr_feed_button.label = f"SSR {ssr_feed_prob}%"



  if (
    view.player_data['level'] == RUB_DOLL['max_level'] and
    view.player_data['doll'] == 'r'
  ):
    view.sr5_on = True
    view.add_item(view.r_to_sr_button)

  if view.player_data['doll'] == 'r':
    embed.color=discord.Colour.green()
  else:
    embed.color=discord.Colour.purple()
  


  true_or_false = view.player_data['level'] >= RUB_DOLL["max_level"]

  view.r_feed_button.disabled = true_or_false
  view.sr_feed_button.disabled = true_or_false
  view.ssr_feed_button.disabled = true_or_false

  try:
    if interaction.response.is_done():
      await interaction.edit_original_response(embed=embed, view=view)
    else:
      await interaction.response.edit_message(embed=embed, view=view)
  except discord.NotFound:
    pass
    

  view.message = await interaction.original_response()





class rub_doll_button2(discord.ui.Button):
  def __init__(self, view_, label="SR開始"):
    super().__init__(style=discord.ButtonStyle.primary, label=label)
    self.view_ = view_  

    self.now_r = True  
    
  async def callback(self, interaction):


    if interaction.user.id != self.view.user_id:
      await interaction.response.defer(ephemeral=True)
      return


    if self.now_r:
      self.view.player_data['doll'] = "sr"
      self.label = "R開始"
      self.style = discord.ButtonStyle.success
      self.now_r = False
    else:
      self.view.player_data['doll'] = "r"
      self.label = "SR開始"
      self.style = discord.ButtonStyle.primary
      self.now_r = True

    await update_message(self.view, interaction)


class rub_doll_button3(discord.ui.Button):
  def __init__(self, view, label="升級SR"):
    super().__init__(style=discord.ButtonStyle.primary, label=label)
 
  async def callback(self, interaction):


    if interaction.user.id != self.view.user_id:
      await interaction.response.defer(ephemeral=True)
      return  

    self.view.player_data['doll'] = "sr"
    self.view.player_data['level'] = 5
    self.view.player_data['exp'] = 0
    self.view.player_data["last_success"] = False

    self.view.remove_item(self)
     

    await update_message(self.view, interaction)


class rub_doll_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="c", aliases=["擦"])
  @commands.cooldown(rate=1, per=RUB_DOLL["cooldown"], type=commands.BucketType.member)

  async def rub_doll(self, ctx: commands.Context):

    if not RUB_DOLL["enable"]:
      return

    if ctx.channel.id != RUB_DOLL["channel"]:
      return

    user_id = ctx.author.id


    player_data[user_id] = {
      'level': 0,
      'exp': 0,
      'used': {'r': 0, 'sr': 0, 'ssr': 0},
      'start_time': datetime.now(TZ_TA),
      'doll': 'r'
    }


    view = rub_doll_view(user_id, player_data[user_id])
    doll = player_data[user_id]['doll']

    embed = discord.Embed(title=f"擦娃娃 {doll.upper()}")

    level = player_data[user_id]['level']
    exp = player_data[user_id]['exp']
    used = player_data[user_id]['used']

    star, img = get_star_img(level, doll)

    bar = get_bar(exp)

    level_text = star+" "+str(level)+"階級"
    exp_text = str(exp)+"/3000"
    used_text = (
      " ".join([f"{k.upper()}:{v * 10}個" 
      for k, v in player_data[user_id]['used'].items()])
    )
    
    embed.description = (
      level_text+"\n"+
      exp_text+"\n"+
      bar+"\n"+
      "總用數\n"+
      used_text
    )
    embed.color=discord.Colour.green()
    embed.set_thumbnail(url=img)
    embed.timestamp = datetime.now(TZ_TA)
    embed.set_footer(text=str(ctx.author.display_name), icon_url=ctx.author.display_avatar.url)

    view.message = await ctx.send(embed=embed, view=view)



async def setup(bot):
  await bot.add_cog(rub_doll_prefix(bot))
