import pytz
from datetime import datetime
import discord
from discord.ext import commands
from apscheduler.triggers.cron import CronTrigger
from utils.emoji_utils import emoji_text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.load_json import json_data
from config.settings import TZ_TA 

DAILY_EN_LOGIN_REMINDER = json_data['DAILY_EN_LOGIN_REMINDER']
CHANNEL_IDS = json_data['CHANNEL_IDS']

DAILY_EN_LOGIN_REMINDER['channel'] = CHANNEL_IDS[DAILY_EN_LOGIN_REMINDER['channel']]

class daily_en_login_reminder_task(commands.Cog):
	def __init__(self, bot,):
		self.bot = bot
		self.scheduler = bot.scheduler

		self.start_job()

	def start_job(self):
		if not DAILY_EN_LOGIN_REMINDER["enable"]:
			return

		if self.scheduler.get_job("daily_en_login_reminder"):
			self.scheduler.remove_job("daily_en_login_reminder")

		trigger = CronTrigger(
			hour=DAILY_EN_LOGIN_REMINDER["hour"],
			minute=DAILY_EN_LOGIN_REMINDER["minute"],
			timezone=TZ_TA
		)

		self.scheduler.add_job(self.send_reminder, trigger=trigger, id="daily_en_login_reminder")
    
	async def send_reminder(self):

		if not self.bot.is_ready():
			return

		channel = self.bot.get_channel(DAILY_EN_LOGIN_REMINDER["channel"])

		if not channel:
			return

		try:
			content = emoji_text(DAILY_EN_LOGIN_REMINDER["message"], channel.guild)
			await channel.send(content)
		except Exception as e:
			print(f"daily_en_login_reminder_task error {e}")

async def setup(bot: commands.Bot):
  await bot.add_cog(daily_en_login_reminder_task(bot))
