import discord
from discord.ext import commands
from utils.load_json import json_data

VC_JOIN_LEAVE = json_data['VC_JOIN_LEAVE']
CHANNEL_IDS = json_data['CHANNEL_IDS']

VC_JOIN_LEAVE['command'] = CHANNEL_IDS[VC_JOIN_LEAVE['command']]

class vc_join_leave_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  # j1 指令：加入語音頻道
  @commands.command(name="jvc")
  async def join_vc(self, ctx, *, channel_name_or_id: str):

    if not VC_JOIN_LEAVE["enable"]:
      return

    if ctx.channel.id != VC_JOIN_LEAVE["command"]:
      return

    if ctx.guild.voice_client:
      await ctx.guild.voice_client.disconnect(force=True)

    # 嘗試用 ID 找頻道
    try:
      channel_id = int(channel_name_or_id)
      target_channel = discord.utils.get(ctx.guild.voice_channels, id=channel_id)
    except ValueError:
      # 否則用名稱找
      target_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name_or_id)

    if not target_channel:
      return

    # 已在語音頻道就不要重複加入
    if ctx.voice_client:
      await ctx.voice_client.move_to(target_channel)
      await ctx.send(f"Joined {target_channel.name}")
    else:
      await target_channel.connect()
      await ctx.send(f"Joined {target_channel.name}")

  # j2 指令：離開語音頻道
  @commands.command(name="lvc")
  async def leave_vc(self, ctx):

    if not VC_JOIN_LEAVE["enable"]:
      return

    if ctx.channel.id != VC_JOIN_LEAVE["command"]:
      return

    # 讓 bot 離開語音頻道
    if ctx.voice_client:
      channel = ctx.voice_client.channel
      await ctx.voice_client.disconnect()
      await ctx.send(f"Left {channel}")
    else:
      await ctx.send("Not in voice channel")

#COG 加入
async def setup(bot):
  await bot.add_cog(vc_join_leave_prefix(bot))
