import asyncio
from databases import Database

class NewsCollector:
    def __init__(self, db: Database, interval: int = 60):
      """
      
      :param db: 数据库连接
      :param interval: 更新间隔（秒）
      """
      self.db = db
      self.interval = interval
    
    async def collect_news(self):
      """
      
      收集热点新闻
      """
      print("📡 收集热点新闻")
    
    async def run(self):
      """
      启动定时任务
      """
      print(f"⏰ 启动定时任务，每{self.interval}秒更新一次")
      while True:
        try:
          await self.collect_news()
        except Exception as e:
          print(f"❌ 出现异常：{e}")
        finally:
          await asyncio.sleep(self.interval)

async def main():
    DATABASE_URL = "postgresql://postgres:123456@localhost:5432/testdb"
    db = Database(DATABASE_URL)
    await db.connect()

    collector = NewsCollector(db)
    await collector.run()

    await db.close()

if __name__ == "__main__":
    asyncio.run(main())
