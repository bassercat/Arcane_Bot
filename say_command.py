from discord.ext import commands
from utils.channel_utils import get_channel
from utils.load_json import json_data

SAY_COMMAND = json_data['SAY_COMMAND']
CHANNEL_IDS = json_data['CHANNEL_IDS']

SAY_COMMAND['channel'] = CHANNEL_IDS[SAY_COMMAND['channel']]
SAY_COMMAND['command'] = CHANNEL_IDS[SAY_COMMAND['command']]

class say_command_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="s")
  async def s(self, ctx, *args):
    if not SAY_COMMAND["enable"]:
      return

    if ctx.channel.id != SAY_COMMAND["command"] or not args:
      return
    
    target_channel = get_channel(ctx.guild, SAY_COMMAND["channel"])
    if not target_channel:
      return
    message_id = None
    content_start_index = 0


    temp_channel = get_channel(ctx.guild, args[0])
    if temp_channel:
      target_channel = temp_channel
      content_start_index = 1

      if len(args) > 1 and args[1].isdigit() and len(args[1]) >= 10:
        try:
          test_message = await target_channel.fetch_message(int(args[1]))
          message_id = int(args[1])
          content_start_index = 2
        except:
          message_id = None
          content_start_index = 1
    elif args[0].isdigit() and len(args[0]) >= 10:
      try:
        test_message = await target_channel.fetch_message(int(args[0]))
        message_id = int(args[0])
        content_start_index = 1
      except:
        message_id = None
        content_start_index = 0


    content = ' '.join(args[content_start_index:]).strip()
    if not content and not ctx.message.attachments:
      return

    try:
      files = []
      if ctx.message.attachments:
        for attachment in ctx.message.attachments:
          file = await attachment.to_file()
          files.append(file)

      if message_id:
        sent_message = await target_channel.send(content or None, reference=test_message, files=files)
      else:
        sent_message = await target_channel.send(content or None, files=files)
      
      msg_link = f"https://discord.com/channels/{ctx.guild.id}/{target_channel.id}/{sent_message.id}"
      await ctx.send(f"{msg_link}")

    except Exception as e:
      print(f"say_command error {e}")
      
async def setup(bot):
  await bot.add_cog(say_command_prefix(bot))
