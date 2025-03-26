import datetime
from typing import List, Optional
from app.data.db_modules.stock_modules.fund_flows import MoneyflowCntThsData


class MoneyflowCntThsCRUD:
    """
    CRUD operations for THS industry/sector moneyflow data.
    
    Provides methods to create, read, update, and delete THS industry/sector moneyflow records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_moneyflow_cnt_ths(self, data: MoneyflowCntThsData) -> None:
        """
        Create a new THS industry/sector moneyflow record in the database.
        
        Args:
            data (MoneyflowCntThsData): The THS industry/sector moneyflow data to insert
        """
        query = """
            INSERT INTO moneyflow_cnt_ths (
                ts_code, trade_date, name, lead_stock, close_price, pct_change, index_close,
                company_num, pct_change_stock, net_buy_amount, net_sell_amount, net_amount
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_moneyflow_cnt_ths_by_key(self, ts_code: str, trade_date: datetime.date) -> Optional[MoneyflowCntThsData]:
        """
        Retrieve a THS industry/sector moneyflow record by its composite key.
        
        Args:
            ts_code (str): The sector code
            trade_date (datetime.date): The trading date
            
        Returns:
            MoneyflowCntThsData | None: The THS industry/sector moneyflow data if found, None otherwise
        """
        query = "SELECT * FROM moneyflow_cnt_ths WHERE ts_code = $1 AND trade_date = $2"
        row = await self.db.fetchrow(query, ts_code, trade_date)
        return MoneyflowCntThsData(**row) if row else None
    
    async def update_moneyflow_cnt_ths(self, ts_code: str, trade_date: datetime.date, updates: dict) -> None:
        """
        Update a THS industry/sector moneyflow record by its composite key.
        
        Args:
            ts_code (str): The sector code
            trade_date (datetime.date): The trading date
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 3}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE moneyflow_cnt_ths
            SET {set_values}
            WHERE ts_code = $1 AND trade_date = $2
        """
        await self.db.execute(query, ts_code, trade_date, *updates.values())
    
    async def delete_moneyflow_cnt_ths(self, ts_code: str, trade_date: datetime.date) -> None:
        """
        Delete a THS industry/sector moneyflow record by its composite key.
        
        Args:
            ts_code (str): The sector code
            trade_date (datetime.date): The trading date
        """
        query = "DELETE FROM moneyflow_cnt_ths WHERE ts_code = $1 AND trade_date = $2"
        await self.db.execute(query, ts_code, trade_date)
    
    async def get_moneyflow_cnt_ths_by_ts_code(self, ts_code: str, limit: int = 100, offset: int = 0) -> List[MoneyflowCntThsData]:
        """
        Retrieve THS industry/sector moneyflow records by sector code with pagination.
        
        Args:
            ts_code (str): The sector code
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowCntThsData]: List of THS industry/sector moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_cnt_ths 
            WHERE ts_code = $1 
            ORDER BY trade_date DESC 
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, ts_code, limit, offset)
        return [MoneyflowCntThsData(**row) for row in rows]
    
    async def get_moneyflow_cnt_ths_by_date_range(self, ts_code: str, start_date: datetime.date, 
                                               end_date: datetime.date) -> List[MoneyflowCntThsData]:
        """
        Retrieve THS industry/sector moneyflow records by sector code within a date range.
        
        Args:
            ts_code (str): The sector code
            start_date (datetime.date): Start date of the range (inclusive)
            end_date (datetime.date): End date of the range (inclusive)
            
        Returns:
            list[MoneyflowCntThsData]: List of THS industry/sector moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_cnt_ths 
            WHERE ts_code = $1 
            AND trade_date BETWEEN $2 AND $3
            ORDER BY trade_date DESC
        """
        rows = await self.db.fetch(query, ts_code, start_date, end_date)
        return [MoneyflowCntThsData(**row) for row in rows]
    
    async def get_moneyflow_cnt_ths_by_date(self, trade_date: datetime.date, limit: int = 100, 
                                          offset: int = 0) -> List[MoneyflowCntThsData]:
        """
        Retrieve THS industry/sector moneyflow records by trading date with pagination.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowCntThsData]: List of THS industry/sector moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_cnt_ths 
            WHERE trade_date = $1 
            ORDER BY net_amount DESC 
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, trade_date, limit, offset)
        return [MoneyflowCntThsData(**row) for row in rows]
    
    async def get_top_inflow_sectors(self, trade_date: datetime.date, limit: int = 10) -> List[MoneyflowCntThsData]:
        """
        Retrieve sectors with the highest net inflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowCntThsData]: List of THS industry/sector moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_cnt_ths 
            WHERE trade_date = $1 
            ORDER BY net_amount DESC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowCntThsData(**row) for row in rows]
    
    async def get_top_outflow_sectors(self, trade_date: datetime.date, limit: int = 10) -> List[MoneyflowCntThsData]:
        """
        Retrieve sectors with the highest net outflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowCntThsData]: List of THS industry/sector moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_cnt_ths 
            WHERE trade_date = $1 
            ORDER BY net_amount ASC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowCntThsData(**row) for row in rows]
    
    async def get_rising_sectors(self, trade_date: datetime.date, limit: int = 10) -> List[MoneyflowCntThsData]:
        """
        Retrieve sectors with the highest price increase on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowCntThsData]: List of THS industry/sector moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_cnt_ths 
            WHERE trade_date = $1 
            ORDER BY pct_change DESC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowCntThsData(**row) for row in rows]