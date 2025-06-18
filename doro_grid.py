import discord
from discord.ext import commands
from discord.ui import View, Button
import random
from datetime import datetime
import pytz
from utils.emoji_utils import get_emoji_map
from config.settings import TZ_TA 
from utils.load_json import json_data

DORO_GRID = json_data['DORO_GRID']
CHANNEL_IDS = json_data['CHANNEL_IDS']

DORO_GRID['channel'] = CHANNEL_IDS[DORO_GRID['channel']]

class grid_button(Button):
  def __init__(self, row, col, true_value, author_id, parent_view):
    
    super().__init__(style=discord.ButtonStyle.secondary,
      label=parent_view.emoji_map.get(DORO_GRID["default_emoji"], DORO_GRID["default_emoji"]),
      row=row)

    self.true_value = true_value
    self.revealed = False  
    self.author_id = author_id
    self.parent_view = parent_view

  async def callback(self, interaction: discord.Interaction):

    if interaction.user.id != self.author_id:
      await interaction.response.defer(ephemeral=True)
      return

    if self.revealed:
      await interaction.response.defer(ephemeral=True)
      return

    for child in self.parent_view.children:
      if isinstance(child, Button):
        child.disabled = True

    self.label = None  
    self.emoji = self.true_value  
    self.style = discord.ButtonStyle.secondary  
    self.revealed = True  
    self.disabled = True  


    self.parent_view.flipped_count += 1

    if getattr(self.true_value, "name", self.true_value) == DORO_GRID["true_emoji"]:
      self.style = discord.ButtonStyle.primary

      for child in self.parent_view.children:
        if isinstance(child, Button):
          child.disabled = True

      embed = interaction.message.embeds[0]
      embed.description = f"{self.parent_view.flipped_count}/25"
      embed.set_thumbnail(url=DORO_GRID["win_img"])
      embed.color = discord.Color.gold()

      await interaction.response.edit_message(embed=embed, view=self.parent_view)
      return


    embed = interaction.message.embeds[0]
    embed.description = f"{self.parent_view.flipped_count}/25"

    for child in self.parent_view.children:
      if isinstance(child, Button) and not getattr(child, "revealed", False):
        child.disabled = False 

    await interaction.response.edit_message(embed=embed, view=self.parent_view)


class doro_grid_view(View):
  def __init__(self, author_id, emoji_map, ctx):


    super().__init__(timeout=DORO_GRID["view_timeout"])  
    self.author_id = author_id


    self.emoji_map = emoji_map

    self.flipped_count = 0  


    items = (
      [emoji_map.get(DORO_GRID["true_emoji"], DORO_GRID["true_emoji"])] +
      [emoji_map.get(DORO_GRID["false_emoji"], DORO_GRID["false_emoji"])] * 24
    )
    random.shuffle(items)

    self.grid = [items[i * 5:(i + 1) * 5] for i in range(5)]


    for row in range(5):
      for col in range(5):
        value = self.grid[row][col]

        self.add_item(grid_button(row=row, col=col, true_value=value,
          author_id=author_id, parent_view=self))
  

    self.message = None

  async def on_timeout(self):

    for child in self.children:
      child.disabled = True
    try:
      if self.message:
        await self.message.edit(view=self)
    except Exception as e:
      print(f"doro_grid_view error {e}")



class doro_grid_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="p", aliases=["玩"])
  @commands.cooldown(rate=1, per=DORO_GRID["cooldown"], type=commands.BucketType.member)
  async def run(self, ctx):

    if not DORO_GRID["enable"]:
      return

    if ctx.channel.id != DORO_GRID["channel"]:
      return
    


    emoji_map = get_emoji_map(ctx.guild)


    embed = discord.Embed(
      title="尋找金Doro",
      description="0/25"
    )
    embed.set_thumbnail(url=DORO_GRID["lose_img"])  
    embed.timestamp = datetime.now(TZ_TA)
    embed.set_footer(text=str(ctx.author.display_name), icon_url=ctx.author.display_avatar.url)


    view = doro_grid_view(ctx.author.id, emoji_map, ctx)
    message = await ctx.send(embed=embed, view=view)

    view.message = message  




async def setup(bot):
  await bot.add_cog(doro_grid_prefix(bot))
