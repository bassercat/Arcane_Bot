import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, button
from utils.load_json import json_data

GACHA = json_data['GACHA']
GACHA_INFO = json_data['GACHA_INFO']
CHANNEL_IDS = json_data['CHANNEL_IDS']

GACHA_INFO['channel'] = CHANNEL_IDS[GACHA_INFO['channel']]

GACHA_INFO['total_ssr_pilgrims'] = len(GACHA['pool']["ssr_pilgrims"])
GACHA_INFO['total_ssr_others'] = len(GACHA['pool']["ssr_others"])




def prob_check_embed() -> discord.Embed:
  prob_check_embed = discord.Embed(
    title="抽卡機率",

  )
  prob_check_embed.add_field(name="本期Pick up", value=", ".join(GACHA['pool']["ssr_pickup"]), inline=False)
  prob_check_embed.add_field(name="抽卡次數 冷卻時間", value=f"{GACHA['max_gacha']} 次 CD {GACHA['cooldown']} 秒", inline=False)
  prob_check_embed.add_field(name="基本機率", value=f"R:{GACHA['r_prob']*100:.0f}%  SR:{GACHA['sr_prob']*100:.0f}%  SSR:{GACHA['ssr_prob']*100:.0f}%", inline=False)
  prob_check_embed.add_field(name="SSR個別機率", value=(
    f"Pickup:{GACHA['ssr_pickup_prob']*100:.0f}%\n"
    f"朝聖超標準:{GACHA['ssr_pilgrims_prob']*100:.1f}%\n"
    f"剩餘SSR:{GACHA['ssr_others_prob']*100:.1f}%"
  ), inline=False)
  prob_check_embed.add_field(name="SSR數量", value=(
    f"朝聖超標準共{GACHA_INFO['total_ssr_pilgrims']}隻\n"
    f"剩餘SSR共{GACHA_INFO['total_ssr_others']}隻"
  ), inline=False)
  prob_check_embed.add_field(name="SSR平均機率", value=(
    f"每隻朝聖超標準機率為{GACHA['ssr_pilgrims_prob']/GACHA_INFO['total_ssr_pilgrims']*100:.4f}%\n"
    f"每隻剩餘SSR機率為{GACHA['ssr_others_prob']/GACHA_INFO['total_ssr_others']*100:.4f}%"
  ), inline=False)
  return prob_check_embed

def gacha_pool_embed() -> discord.Embed:
  gacha_pool_embed = discord.Embed(
    title="卡池一覽",

  )
  gacha_pool_embed.add_field(name="本期Pick up", value=f", ".join(GACHA['pool']["ssr_pickup"]), inline=False)
  gacha_pool_embed.add_field(name="SSR朝聖超標準", value=f"```{', '.join(GACHA['pool']['ssr_pilgrims'])}```", inline=False)
  gacha_pool_embed.add_field(name="剩餘SSR", value=f"```{', '.join(GACHA['pool']['ssr_others'])}```", inline=False)
  gacha_pool_embed.add_field(name="SR", value=f"```{', '.join(GACHA['pool']['sr'])}```", inline=False)
  gacha_pool_embed.add_field(name="R", value=f"```{', '.join(GACHA['pool']['r'])}```", inline=False)
  gacha_pool_embed.set_footer(text="目前所有卡池角色")
  return gacha_pool_embed


class gacha_info_view(View):
  def __init__(self):
    super().__init__(timeout=GACHA_INFO["view_timeout"])

    self.message = None  


    for child in self.children:
      if isinstance(child, Button):
 
        if child.label == "抽卡機率":  
          child.style = discord.ButtonStyle.primary
          child.disabled = True
        else:
          child.style = discord.ButtonStyle.secondary
          child.disabled = False

  @button(label="抽卡機率", style=discord.ButtonStyle.primary)
  async def prob_button(self, interaction: discord.Interaction, button: Button):

    for child in self.children:
      if isinstance(child, Button):
        if child == button:
          child.style = discord.ButtonStyle.primary

          child.disabled = True   
        else:
          child.style = discord.ButtonStyle.secondary

          child.disabled = False  
    await interaction.response.edit_message(embed=prob_check_embed(), view=self)

  @button(label="卡池一覽", style=discord.ButtonStyle.secondary)
  async def list_button(self, interaction: discord.Interaction, button: Button):

    for child in self.children:
      if isinstance(child, Button):
        if child == button:
          child.style = discord.ButtonStyle.primary

          child.disabled = True   
        else:
          child.style = discord.ButtonStyle.secondary

          child.disabled = False 
    await interaction.response.edit_message(embed=gacha_pool_embed(), view=self)

  async def on_timeout(self):

    for child in self.children:
      child.disabled = True

    try:
      if self.message:
        await self.message.edit(view=self)
    except Exception as e:
      print(f"gacha_info_view error {e}")
  
class gacha_info_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot



  @commands.command(name="prob", description="prob")
  @commands.cooldown(rate=1, per=GACHA_INFO["cooldown"], type=commands.BucketType.guild)
  async def prob(self, ctx: commands.Context):


    if not GACHA_INFO["enable"]:
      return

    if ctx.channel.id != GACHA_INFO["channel"]:
      return

    view = gacha_info_view()
    try:
      message = await ctx.send(embed=prob_check_embed(), view=view)
      view.message = message
    except Exception as e:
      print(f"gacha_info_prefix error {e}")

async def setup(bot):
  await bot.add_cog(gacha_info_prefix(bot))
