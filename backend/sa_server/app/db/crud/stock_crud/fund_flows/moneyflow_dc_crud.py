import datetime
from typing import List, Optional
from app.data.db_modules.stock_modules.fund_flows.moneyflow_dc import MoneyflowDcData


class MoneyflowDcCRUD:
    """
    CRUD operations for large transaction (DC) stock moneyflow data.
    
    Provides methods to create, read, update, and delete DC moneyflow records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_moneyflow_dc(self, data: MoneyflowDcData) -> None:
        """
        Create a new DC moneyflow record in the database.
        
        Args:
            data (MoneyflowDcData): The DC moneyflow data to insert
        """
        query = """
            INSERT INTO moneyflow_dc (
                ts_code, trade_date, name, pct_change, close, net_amount, net_amount_rate,
                buy_elg_amount, buy_elg_amount_rate, buy_lg_amount, buy_lg_amount_rate,
                buy_md_amount, buy_md_amount_rate, buy_sm_amount, buy_sm_amount_rate
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_moneyflow_dc_by_key(self, ts_code: str, trade_date: datetime.date) -> Optional[MoneyflowDcData]:
        """
        Retrieve a DC moneyflow record by its composite key.
        
        Args:
            ts_code (str): The stock code
            trade_date (datetime.date): The trading date
            
        Returns:
            MoneyflowDcData | None: The DC moneyflow data if found, None otherwise
        """
        query = "SELECT * FROM moneyflow_dc WHERE ts_code = $1 AND trade_date = $2"
        row = await self.db.fetchrow(query, ts_code, trade_date)
        return MoneyflowDcData(**row) if row else None
    
    async def update_moneyflow_dc(self, ts_code: str, trade_date: datetime.date, updates: dict) -> None:
        """
        Update a DC moneyflow record by its composite key.
        
        Args:
            ts_code (str): The stock code
            trade_date (datetime.date): The trading date
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 3}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE moneyflow_dc
            SET {set_values}
            WHERE ts_code = $1 AND trade_date = $2
        """
        await self.db.execute(query, ts_code, trade_date, *updates.values())
    
    async def delete_moneyflow_dc(self, ts_code: str, trade_date: datetime.date) -> None:
        """
        Delete a DC moneyflow record by its composite key.
        
        Args:
            ts_code (str): The stock code
            trade_date (datetime.date): The trading date
        """
        query = "DELETE FROM moneyflow_dc WHERE ts_code = $1 AND trade_date = $2"
        await self.db.execute(query, ts_code, trade_date)
    
    async def get_moneyflow_dc_by_ts_code(self, ts_code: str, limit: int = 100, offset: int = 0) -> List[MoneyflowDcData]:
        """
        Retrieve DC moneyflow records by stock code with pagination.
        
        Args:
            ts_code (str): The stock code
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowDcData]: List of DC moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_dc 
            WHERE ts_code = $1 
            ORDER BY trade_date DESC 
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, ts_code, limit, offset)
        return [MoneyflowDcData(**row) for row in rows]
    
    async def get_moneyflow_dc_by_date_range(self, ts_code: str, start_date: datetime.date, 
                                          end_date: datetime.date) -> List[MoneyflowDcData]:
        """
        Retrieve DC moneyflow records by stock code within a date range.
        
        Args:
            ts_code (str): The stock code
            start_date (datetime.date): Start date of the range (inclusive)
            end_date (datetime.date): End date of the range (inclusive)
            
        Returns:
            list[MoneyflowDcData]: List of DC moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_dc 
            WHERE ts_code = $1 
            AND trade_date BETWEEN $2 AND $3
            ORDER BY trade_date DESC
        """
        rows = await self.db.fetch(query, ts_code, start_date, end_date)
        return [MoneyflowDcData(**row) for row in rows]
    
    async def get_moneyflow_dc_by_date(self, trade_date: datetime.date, limit: int = 100, 
                                     offset: int = 0) -> List[MoneyflowDcData]:
        """
        Retrieve DC moneyflow records by trading date with pagination.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowDcData]: List of DC moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_dc 
            WHERE trade_date = $1 
            ORDER BY net_amount DESC 
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, trade_date, limit, offset)
        return [MoneyflowDcData(**row) for row in rows]
    
    async def get_top_inflow(self, trade_date: datetime.date, limit: int = 10) -> List[MoneyflowDcData]:
        """
        Retrieve stocks with the highest net inflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowDcData]: List of DC moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_dc 
            WHERE trade_date = $1 
            ORDER BY net_amount DESC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowDcData(**row) for row in rows]
    
    async def get_top_outflow(self, trade_date: datetime.date, limit: int = 10) -> List[MoneyflowDcData]:
        """
        Retrieve stocks with the highest net outflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowDcData]: List of DC moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_dc 
            WHERE trade_date = $1 
            ORDER BY net_amount ASC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowDcData(**row) for row in rows]

    async def get_top_elg_inflow(self, trade_date: datetime.date, limit: int = 10) -> List[MoneyflowDcData]:
        """
        Retrieve stocks with the highest extra-large order net inflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowDcData]: List of DC moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_dc 
            WHERE trade_date = $1 
            ORDER BY buy_elg_amount DESC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowDcData(**row) for row in rows]
        
    async def get_top_lg_inflow(self, trade_date: datetime.date, limit: int = 10) -> List[MoneyflowDcData]:
        """
        Retrieve stocks with the highest large order net inflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowDcData]: List of DC moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_dc 
            WHERE trade_date = $1 
            ORDER BY buy_lg_amount DESC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowDcData(**row) for row in rows]