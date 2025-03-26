import datetime
from typing import List, Optional
from app.data.db_modules.stock_modules.fund_flows.moneyflow_ths import MoneyflowThsData


class MoneyflowThsCRUD:
    """
    CRUD operations for THS stock moneyflow data.
    
    Provides methods to create, read, update, and delete THS moneyflow records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_moneyflow_ths(self, data: MoneyflowThsData) -> None:
        """
        Create a new THS moneyflow record in the database.
        
        Args:
            data (MoneyflowThsData): The THS moneyflow data to insert
        """
        query = """
            INSERT INTO moneyflow_ths (
                ts_code, trade_date, name, pct_change, latest, net_amount, net_d5_amount,
                buy_lg_amount, buy_lg_amount_rate, buy_md_amount, buy_md_amount_rate,
                buy_sm_amount, buy_sm_amount_rate
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_moneyflow_ths_by_key(self, ts_code: str, trade_date: datetime.date) -> Optional[MoneyflowThsData]:
        """
        Retrieve a THS moneyflow record by its composite key.
        
        Args:
            ts_code (str): The stock code
            trade_date (datetime.date): The trading date
            
        Returns:
            MoneyflowThsData | None: The THS moneyflow data if found, None otherwise
        """
        query = "SELECT * FROM moneyflow_ths WHERE ts_code = $1 AND trade_date = $2"
        row = await self.db.fetchrow(query, ts_code, trade_date)
        return MoneyflowThsData(**row) if row else None
    
    async def update_moneyflow_ths(self, ts_code: str, trade_date: datetime.date, updates: dict) -> None:
        """
        Update a THS moneyflow record by its composite key.
        
        Args:
            ts_code (str): The stock code
            trade_date (datetime.date): The trading date
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 3}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE moneyflow_ths
            SET {set_values}
            WHERE ts_code = $1 AND trade_date = $2
        """
        await self.db.execute(query, ts_code, trade_date, *updates.values())
    
    async def delete_moneyflow_ths(self, ts_code: str, trade_date: datetime.date) -> None:
        """
        Delete a THS moneyflow record by its composite key.
        
        Args:
            ts_code (str): The stock code
            trade_date (datetime.date): The trading date
        """
        query = "DELETE FROM moneyflow_ths WHERE ts_code = $1 AND trade_date = $2"
        await self.db.execute(query, ts_code, trade_date)
    
    async def get_moneyflow_ths_by_ts_code(self, ts_code: str, limit: int = 100, offset: int = 0) -> List[MoneyflowThsData]:
        """
        Retrieve THS moneyflow records by stock code with pagination.
        
        Args:
            ts_code (str): The stock code
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowThsData]: List of THS moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_ths 
            WHERE ts_code = $1 
            ORDER BY trade_date DESC 
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, ts_code, limit, offset)
        return [MoneyflowThsData(**row) for row in rows]
    
    async def get_moneyflow_ths_by_date_range(self, ts_code: str, start_date: datetime.date, 
                                          end_date: datetime.date) -> List[MoneyflowThsData]:
        """
        Retrieve THS moneyflow records by stock code within a date range.
        
        Args:
            ts_code (str): The stock code
            start_date (datetime.date): Start date of the range (inclusive)
            end_date (datetime.date): End date of the range (inclusive)
            
        Returns:
            list[MoneyflowThsData]: List of THS moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_ths 
            WHERE ts_code = $1 
            AND trade_date BETWEEN $2 AND $3
            ORDER BY trade_date DESC
        """
        rows = await self.db.fetch(query, ts_code, start_date, end_date)
        return [MoneyflowThsData(**row) for row in rows]
    
    async def get_moneyflow_ths_by_date(self, trade_date: datetime.date, limit: int = 100, 
                                      offset: int = 0) -> List[MoneyflowThsData]:
        """
        Retrieve THS moneyflow records by trading date with pagination.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowThsData]: List of THS moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_ths 
            WHERE trade_date = $1 
            ORDER BY net_amount DESC 
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, trade_date, limit, offset)
        return [MoneyflowThsData(**row) for row in rows]
    
    async def get_top_inflow(self, trade_date: datetime.date, limit: int = 10) -> List[MoneyflowThsData]:
        """
        Retrieve stocks with the highest net inflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowThsData]: List of THS moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_ths 
            WHERE trade_date = $1 
            ORDER BY net_amount DESC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowThsData(**row) for row in rows]
    
    async def get_top_outflow(self, trade_date: datetime.date, limit: int = 10) -> List[MoneyflowThsData]:
        """
        Retrieve stocks with the highest net outflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowThsData]: List of THS moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_ths 
            WHERE trade_date = $1 
            ORDER BY net_amount ASC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowThsData(**row) for row in rows]

    async def get_top_d5_inflow(self, trade_date: datetime.date, limit: int = 10) -> List[MoneyflowThsData]:
        """
        Retrieve stocks with the highest 5-day main force net inflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowThsData]: List of THS moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_ths 
            WHERE trade_date = $1 
            ORDER BY net_d5_amount DESC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowThsData(**row) for row in rows]