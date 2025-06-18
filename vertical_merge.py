import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image
import io
import aiohttp
from utils.load_json import json_data
from datetime import datetime, timedelta

VERTICAL_MERGE = json_data['VERTICAL_MERGE']
MAIN = json_data['MAIN']
CHANNEL_IDS = json_data['CHANNEL_IDS']

if isinstance(VERTICAL_MERGE['channel'], str):
  VERTICAL_MERGE['channel'] = CHANNEL_IDS[VERTICAL_MERGE['channel']]

class vertical_merge_cog(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.cooldown_seconds = VERTICAL_MERGE['cooldown']
    self.user_cooldowns = {}

@app_commands.guilds(discord.Object(id=MAIN["guild_id"]))
@app_commands.context_menu(name="Vertical Merge")
async def vertical_merge(interaction: discord.Interaction, message: discord.Message):
  cog = interaction.client.get_cog("vertical_merge_cog")
  try:  
    await interaction.response.defer(thinking=True)

    if not VERTICAL_MERGE["enable"]:
      return

    if interaction.channel_id != VERTICAL_MERGE["channel"]:
      return

    now = datetime.utcnow()
    last_time = cog.user_cooldowns.get(interaction.user.id)

    if last_time and last_time > now:
      left = (last_time - now).total_seconds()
      await interaction.response.send_message(f"{left:.1f} 秒", ephemeral=True)
      return

    cog.user_cooldowns[interaction.user.id] = now + timedelta(seconds=cog.cooldown_seconds)

    images = []
    async with aiohttp.ClientSession() as session:
      for attachment in message.attachments:
        if attachment.content_type and attachment.content_type.startswith("image"):
          async with session.get(attachment.url) as resp:
            if resp.status == 200:
              data = await resp.read()
              img = Image.open(io.BytesIO(data)).convert("RGBA")
              images.append(img)

    if len(images) < 2:
      return

    min_width = min(img.width for img in images)

    cropped_imgs = []
    for img in images:
      if img.width > min_width:
        diff = img.width - min_width
        left_crop = diff // 2
        right_crop = diff - left_crop
        box = (left_crop, 0, img.width - right_crop, img.height)
        cropped = img.crop(box)
        cropped_imgs.append(cropped)
      else:
        cropped_imgs.append(img)

    total_height = sum(img.height for img in cropped_imgs)

    merged_img = Image.new("RGB", (min_width, total_height), (255, 255, 255))

    y_offset = 0
    for img in cropped_imgs:
      if img.mode == "RGBA":
        img = img.convert("RGB")
      merged_img.paste(img, (0, y_offset))
      y_offset += img.height

    img_bytes = io.BytesIO()
    merged_img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    file = discord.File(fp=img_bytes, filename="merged.jpg")
    await interaction.followup.send(file=file)
    
  except Exception as e:
    if not interaction.response.is_done():
      await interaction.response.send_message(f"Error", ephemeral=True)
      print(f"vertical_merge error {e}")
    else:
      await interaction.followup.send(f"Error", ephemeral=True)
      print(f"vertical_merge error {e}") 

async def setup(bot):
    await bot.add_cog(vertical_merge_cog(bot))
    bot.tree.add_command(vertical_merge, guild=discord.Object(id=MAIN["guild_id"]))
