import discord
from discord.ext import commands
import edge_tts
import asyncio
import os
from utils.load_json import json_data

VC_SPEAK = json_data['VC_SPEAK']
CHANNEL_IDS = json_data['CHANNEL_IDS']

VC_SPEAK['command'] = CHANNEL_IDS[VC_SPEAK['command']]

class vc_speak_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="vcs")
  async def speak(self, ctx: commands.Context, *, text: str = ""):

    if not VC_SPEAK["enable"]:
      return

    if ctx.channel.id != VC_SPEAK["command"] or not text.strip():
      return
    
    voice = "zh-TW-HsiaoYuNeural"  

    voice_path = VC_SPEAK['voice_path']

    try:

      vc = ctx.guild.voice_client

      if not vc:
        return

      if vc.is_playing():
        os.remove(voice_path)
        return


      communicate = edge_tts.Communicate(text, voice=voice)
      await communicate.save(voice_path)

      if not os.path.exists(voice_path):
        return


      vc.play(discord.FFmpegPCMAudio(source=voice_path, options='-loglevel error'))

      while vc.is_playing():
          await asyncio.sleep(1)
    finally:
      if os.path.exists(voice_path):
          os.remove(voice_path)

    await ctx.send("Ended vcs")



  @commands.command(name="vcss")
  async def stop(self, ctx: commands.Context):

    if not VC_SPEAK["enable"]:
      return

    if ctx.channel.id != VC_SPEAK["command"]:
      return

    vc = ctx.guild.voice_client
    if not vc or not vc.is_connected():
      return

    if vc.is_playing():
      vc.stop()
      await ctx.send("Stopped vcs")

    voice_path = VC_SPEAK.get('voice_path', 'voice.mp3')
    if os.path.exists(voice_path):
      try:
        os.remove(voice_path)
      except Exception as e:
        print(f"vc_stop error {e}")

async def setup(bot):
  await bot.add_cog(vc_speak_prefix(bot))
