from app.data.ui_modules import IndexBaseData


class IndexBaseDataCRUD:
  """
  
  """

  def __init__(self, db):
    self.db = db

  async def create_index(self, data: IndexBaseData) -> None:
    query = """
      INSERT INTO index_base (
        ts_code, name, fullname, market, publisher, index_type, category,
        base_date, base_point, list_date, weight_rule, desc, exp_date
      ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
      )
    """
    await self.db.execute(query, *data.dict().values())

  async def get_index_by_code(self, ts_code: str) -> IndexBaseData | None:
    query = "SELECT * FROM index_base WHERE ts_code = $1"
    row = await self.db.fetchrow(query, ts_code)
    return IndexBaseData(**row) if row else None
  
  async def update_index(self, ts_code: str, updates: dict) -> None:
    set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
    query = f"""
      UPDATE index_base
      SET {set_values}
      WHERE ts_code = $1
    """
    await self.db.execute(query, ts_code, *updates.values())
  
  async def delete_index(self, ts_code: str) -> None:
    query = "DELETE FROM index_base WHERE ts_code = $1"
    await self.db.execute(query, ts_code)