import asyncio
from datetime import datetime
from app.utils.logger import logger
from app.db.connection import Database
from apscheduler.triggers.cron import CronTrigger
from app.utils.notifier import send_email_notification
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class DailyTask:
  def __init__(self, db: Database, hour: int = 0, minute: int = 0, max_retries: int = 3):
    """
    
    :param db: 数据库连接
    :param hour: 每日触发的小时（0~23）
    :param minute: 每日触发的分钟（0~59）
    :param max_retries: 最大重试次数
    """
    self.db = db
    self.hour = hour
    self.minute = minute
    self.max_retries = max_retries
    self.scheduler = AsyncIOScheduler()
  
  async def update_daily_data(self):
    """
    
    更新每日数据
    """
    retries = 0
    while retries < self.max_retries:

      try:
        # 任务逻辑
        logger.info(f"✅ [INFO] 数据更新成功: {datetime.now()}")
        return
      except Exception as e:
        retries += 1
        logger.error(f"❌ [ERROR] 数据更新失败: {e}")
        if retries == self.max_retries:
          await send_email_notification(
            "数据更新失败",
            f"任务失败，时间：{datetime.now()}\n错误信息：{e}"
          )
        # 重试间隔
        await asyncio.sleep(5)
  
  def start(self):
    """
    启动定时任务
    """
    self.scheduler.add_job(
      self.update_daily_data,
      CronTrigger(hour=self.hour, minute=self.minute)
    )
    print(f"⏰ 启动定时任务，每日 {self.hour} 时 {self.minute} 分更新")
    self.scheduler.start()

async def main():
  DATABASE_URL = "postgresql://postgres:123456@localhost:5432/testdb"
  db = Database(DATABASE_URL)
  await db.connect()

  daily_task = DailyTask(db, hour=8, minute=0)
  daily_task.start()

  while True:
    await asyncio.sleep(1)

if __name__ == "__main__":
  asyncio.run(main())

    