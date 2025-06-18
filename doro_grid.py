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

# 按鈕類別，代表 Grid 盤上每個格子上的一個按鈕
class grid_button(Button):
  def __init__(self, row, col, true_value, author_id, parent_view):
    
    # 初始按鈕標籤為DORO_GRID["default_emoji"]，樣式為 secondary
    super().__init__(style=discord.ButtonStyle.secondary,
      label=parent_view.emoji_map.get(DORO_GRID["default_emoji"], DORO_GRID["default_emoji"]),
      row=row)

    # 按鈕對應的正確 emoji 物件
    self.true_value = true_value
    # 是否已被揭示（點擊過）
    self.revealed = False  
    # 指令發出者 ID，用於限制只有指令者能點擊按鈕
    self.author_id = author_id
    # 此按鈕所屬的 View 物件，用來更新整體狀態與 embed
    self.parent_view = parent_view

  # 按鈕被點擊時觸發的回調函式
  async def callback(self, interaction: discord.Interaction):

    # 只有指令發出者本人能點按鈕，其他人點擊無效
    if interaction.user.id != self.author_id:
      await interaction.response.defer(ephemeral=True)
      return

    # 如果按鈕已被揭示過，忽略點擊，回覆 deferring 防止錯誤
    if self.revealed:
      await interaction.response.defer(ephemeral=True)
      return

    # 防連點 點擊後先 disable 所有按鈕
    for child in self.parent_view.children:
      if isinstance(child, Button):
        child.disabled = True

    # 揭示按鈕內容
    # 移除標籤
    self.label = None  
    # 顯示對應 emoji（真實內容）
    self.emoji = self.true_value  
    # 按鈕樣式設定
    self.style = discord.ButtonStyle.secondary  
    # 標記已揭示
    self.revealed = True  
    # 按鈕點過就不能再點
    self.disabled = True  

    # 翻開計數+1
    self.parent_view.flipped_count += 1

    # 若揭示到 true，遊戲結束
    if getattr(self.true_value, "name", self.true_value) == DORO_GRID["true_emoji"]:
      self.style = discord.ButtonStyle.primary
      # 停用所有按鈕，防止繼續點擊
      for child in self.parent_view.children:
        if isinstance(child, Button):
          child.disabled = True
      # 更新 embed，描述顯示目前翻開數，並換成true圖片
      embed = interaction.message.embeds[0]
      embed.description = f"{self.parent_view.flipped_count}/25"
      embed.set_thumbnail(url=DORO_GRID["win_img"])
      embed.color = discord.Color.gold()
      # 更新訊息
      await interaction.response.edit_message(embed=embed, view=self.parent_view)
      return

    # 若無，更新 embed 描述翻開數
    embed = interaction.message.embeds[0]
    embed.description = f"{self.parent_view.flipped_count}/25"

    # 重新啟用尚未揭示的按鈕，讓玩家繼續點擊
    for child in self.parent_view.children:
      if isinstance(child, Button) and not getattr(child, "revealed", False):
        child.disabled = False 
        

    # 編輯訊息，更新 embed 和按鈕狀態
    await interaction.response.edit_message(embed=embed, view=self.parent_view)


# 控制整個 5x5 按鈕盤的 View 類別
# emoji_map: 伺服器中名稱對應 emoji 物件的字典
# ctx: 命令上下文，用於日後擴展功能（例如發訊息等）
class doro_grid_view(View):
  def __init__(self, author_id, emoji_map, ctx):


    # 設定此 View 不會自動過期
    super().__init__(timeout=DORO_GRID["view_timeout"])  
    self.author_id = author_id

    #繼承
    self.emoji_map = emoji_map

    # 已翻開按鈕計數器，初始為0
    self.flipped_count = 0  

    # 產生一個 true 與 24 個 false ，並打亂順序
    items = (
      [emoji_map.get(DORO_GRID["true_emoji"], DORO_GRID["true_emoji"])] +
      [emoji_map.get(DORO_GRID["false_emoji"], DORO_GRID["false_emoji"])] * 24
    )
    random.shuffle(items)

    # 分割成 5x5 二維列表
    self.grid = [items[i * 5:(i + 1) * 5] for i in range(5)]

    # 建立 grid_button 按鈕，加入 View 中
    for row in range(5):
      for col in range(5):
        value = self.grid[row][col]
        # 新增 parent_view 參數，傳自己給按鈕
        self.add_item(grid_button(row=row, col=col, true_value=value,
          author_id=author_id, parent_view=self))
  
    # 預設沒有 message，之後會存
    self.message = None

  async def on_timeout(self):
    # 禁用所有按鈕
    for child in self.children:
      child.disabled = True
    try:
      if self.message:
        await self.message.edit(view=self)
    except Exception as e:
      print(f"doro_grid_view error {e}")


# Cog 類別，/p 或 /玩 指令
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
    

    # 建立名稱對應 emoji 物件字典，方便從伺服器表情中抓取需要用的 emoji
    emoji_map = get_emoji_map(ctx.guild)

    # 建立 embed 物件，初始描述為 0/25 按鈕已翻開
    embed = discord.Embed(
      title="尋找金Doro",
      description="0/25"
    )
    embed.set_thumbnail(url=DORO_GRID["lose_img"])  
    embed.timestamp = datetime.now(TZ_TA)
    embed.set_footer(text=str(ctx.author.display_name), icon_url=ctx.author.display_avatar.url)

    # 發送訊息並附上 GridView 視圖，讓玩家開始互動遊戲
    #await ctx.send(embed=embed, view=doro_grid_view(ctx.author.id, emoji_map, ctx))
    view = doro_grid_view(ctx.author.id, emoji_map, ctx)
    message = await ctx.send(embed=embed, view=view)
    # 記錄訊息物件
    view.message = message  




# 載入 Cog
async def setup(bot):
  await bot.add_cog(doro_grid_prefix(bot))