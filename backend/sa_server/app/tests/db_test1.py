import asyncio
from app.db.connection import Database
from app.db.cn_index_crud import CNIndexCRUD
from app.data.modules import CNIndexBaseData

# 数据库连接
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/testdb"

async def main():

  db = Database(DATABASE_URL)
  await db.connect()
  crud = CNIndexCRUD(db)

  sample_data = CNIndexBaseData(
    ts_code="000001.SH",
    name="上证指数",
    fullname="上证指数",
    market="SSE",
    publisher="中证公司",
    index_type="综合指数",
    category="规模指数",
    base_date="1991-07-15",
    base_point=100.0,
    list_date="1991-07-15",
    weight_rule="总市值加权",
    desc="上证指数",
    exp_date=None
  )

  await crud.create_index(sample_data)
  print("✅ 创建成功")

  index_data = await crud.get_index_by_code("000001.SH")
  print(f"🔍 查询结果：{index_data}")

  await crud.update_index("000001.SH", {"desc": "上证综指"})
  print("✅ 更新成功")

  await crud.delete_index("000001.SH")
  print("✅ 删除成功")

  await db.close()

if __name__ == "__main__":
  asyncio.run(main())