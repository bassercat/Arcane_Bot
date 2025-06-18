from discord.ext import commands
from listeners.auto_emoji_react import auto_emoji_react
from listeners.chat_draw_one import chat_draw_one
from listeners.command_conversion import command_conversion

class on_message(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, message):

    if message.author.bot:
      return


    await auto_emoji_react(self.bot, message)
    await chat_draw_one(self.bot, message)
    await command_conversion(self.bot, message)

async def setup(bot):
  await bot.add_cog(on_message(bot))
