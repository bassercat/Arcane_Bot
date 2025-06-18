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

		# 啟動排程任務（此行在 Cog 初始化時執行）
		self.start_job()

	def start_job(self):
		# 如果未啟用提醒功能，則不啟動任務
		if not DAILY_EN_LOGIN_REMINDER["enable"]:
			return

		# 先嘗試移除舊任務，避免重複排程
		if self.scheduler.get_job("daily_en_login_reminder"):
			self.scheduler.remove_job("daily_en_login_reminder")

		# 建立 CronTrigger，指定每天幾點幾分執行（時與分）
		trigger = CronTrigger(
			hour=DAILY_EN_LOGIN_REMINDER["hour"],
			minute=DAILY_EN_LOGIN_REMINDER["minute"],
			timezone=TZ_TA
		)

		# 排程任務加入 scheduler
		self.scheduler.add_job(self.send_reminder, trigger=trigger, id="daily_en_login_reminder")
    
	async def send_reminder(self):

    # 若 bot 尚未就緒，跳過
		if not self.bot.is_ready():
			return

		# 取得指定頻道物件
		channel = self.bot.get_channel(DAILY_EN_LOGIN_REMINDER["channel"])

		if not channel:
			return

		try:
			# 處理訊息內容（把文字中的emoji名稱換成伺服器emoji）
			content = emoji_text(DAILY_EN_LOGIN_REMINDER["message"], channel.guild)
			await channel.send(content)
		except Exception as e:
			print(f"daily_en_login_reminder_task error {e}")

async def setup(bot: commands.Bot):
  await bot.add_cog(daily_en_login_reminder_task(bot))