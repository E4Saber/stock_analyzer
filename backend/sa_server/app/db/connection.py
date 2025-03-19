import asyncpg

class Database:

  def __init__(self, dsn: str):
    self.dsn = dsn
    self.pool = None

  async def connect(self):
    self.pool = await asyncpg.create_pool(self.dsn)
  
  async def close(self):
    if self.pool:
      await self.pool.close()
  
  async def execute(self, query, *args):
    async with self.pool.acquire() as conn:
      return await conn.execute(query, *args)
  
  async def fetch(self, query, *args):
    async with self.pool.acquire() as conn:
      return await conn.fetch(query, *args)
  
  async def fetchrow(self, query, *args):
    async with self.pool.acquire() as conn:
      return await conn.fetchrow(query, *args)
