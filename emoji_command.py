import discord
from discord.ext import commands
from utils.channel_utils import get_channel
from utils.load_json import json_data
EMOJI_COMMAND = json_data['EMOJI_COMMAND']
CHANNEL_IDS = json_data['CHANNEL_IDS']

EMOJI_COMMAND['channel'] = CHANNEL_IDS[EMOJI_COMMAND['channel']]
EMOJI_COMMAND['command'] = CHANNEL_IDS[EMOJI_COMMAND['command']]

class emoji_command_prefix(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  @commands.command(name='e')
  async def e(self, ctx, *args):
    if not EMOJI_COMMAND["enable"]:
      return


    if ctx.channel.id != EMOJI_COMMAND["command"] or len(args) < 2:
      return

    target_channel = get_channel(ctx.guild, EMOJI_COMMAND["channel"])
    if not target_channel:
      return


    temp_channel = get_channel(ctx.guild, args[0])
    if temp_channel:
      target_channel = temp_channel      


      if len(args) > 1 and args[1].isdigit() and len(args[1]) >= 10:
        try:
          target_message = await target_channel.fetch_message(int(args[1]))
          message_id = int(args[1])
          emoji_index = 2
        except:
          return


    elif args[0].isdigit() and len(args[0]) >= 10:
      try:
        target_message = await target_channel.fetch_message(int(args[0]))
        message_id = int(args[0])
        emoji_index = 1
      except:

        return
    else:

      return

    if not target_message:
      return


    emojis = args[emoji_index:]
    
    try:

      reacted_emojis = set()


      for reaction in target_message.reactions:
        async for user in reaction.users():
          if user == self.bot.user:
            reacted_emojis.add(str(reaction.emoji))
            break 


      for emoji_raw in emojis:
        try:
          if emoji_raw in reacted_emojis:
            await target_message.remove_reaction(emoji_raw, self.bot.user)
            reacted_emojis.remove(emoji_raw)
          else:
            await target_message.add_reaction(emoji_raw)
            reacted_emojis.add(emoji_raw)

        except discord.errors.HTTPException as e:

          if "Unknown Emoji" in e.text:
            pass
          else:
            print(f"emoji_command error {e}")
        except Exception as e:
          print(f"emoji_command error {e}")


      msg_link = f"https://discord.com/channels/{ctx.guild.id}/{target_channel.id}/{target_message.id}"

      await ctx.send(f"{msg_link}")

    except Exception as e:
      print(f"emoji_command error {e}")

async def setup(bot):
  await bot.add_cog(emoji_command_prefix(bot))
