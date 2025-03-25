import datetime
from typing import List, Optional
from app.data.db_modules.stock_modules.stock_basic.stk_premarket import StkPremarketData


class StkPremarketCRUD:
    """
    CRUD operations for stock premarket data.
    
    Provides methods to create, read, update, and delete stock premarket records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_premarket(self, data: StkPremarketData) -> None:
        """
        Create a new stock premarket record in the database.
        
        Args:
            data (StkPremarketData): The premarket data to insert
        """
        query = """
            INSERT INTO stk_premarket (
                trade_date, ts_code, total_share, float_share,
                pre_close, up_limit, down_limit
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7
            )
        """
        values = [
            data.trade_date,
            data.ts_code,
            data.total_share,
            data.float_share,
            data.pre_close,
            data.up_limit,
            data.down_limit
        ]
        await self.db.execute(query, *values)

    async def get_premarket(self, trade_date: datetime.date, ts_code: str) -> Optional[StkPremarketData]:
        """
        Retrieve a stock premarket record by its primary key.
        
        Args:
            trade_date (datetime.date): Trading date
            ts_code (str): The TS code of the stock
            
        Returns:
            StkPremarketData | None: The premarket data if found, None otherwise
        """
        query = "SELECT * FROM stk_premarket WHERE trade_date = $1 AND ts_code = $2"
        row = await self.db.fetchrow(query, trade_date, ts_code)
        return StkPremarketData(**row) if row else None
    
    async def update_premarket(self, trade_date: datetime.date, ts_code: str, updates: dict) -> None:
        """
        Update a stock premarket record by its primary key.
        
        Args:
            trade_date (datetime.date): Trading date
            ts_code (str): The TS code of the stock
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 3}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE stk_premarket
            SET {set_values}
            WHERE trade_date = $1 AND ts_code = $2
        """
        await self.db.execute(query, trade_date, ts_code, *updates.values())
    
    async def delete_premarket(self, trade_date: datetime.date, ts_code: str) -> None:
        """
        Delete a stock premarket record by its primary key.
        
        Args:
            trade_date (datetime.date): Trading date
            ts_code (str): The TS code of the stock
        """
        query = "DELETE FROM stk_premarket WHERE trade_date = $1 AND ts_code = $2"
        await self.db.execute(query, trade_date, ts_code)
    
    async def list_premarket_by_date(self, trade_date: datetime.date, limit: int = 100, offset: int = 0) -> List[StkPremarketData]:
        """
        List premarket data for a specific date with pagination.
        
        Args:
            trade_date (datetime.date): Trading date to filter by
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[StkPremarketData]: List of premarket data
        """
        query = """
            SELECT * FROM stk_premarket 
            WHERE trade_date = $1
            ORDER BY ts_code 
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, trade_date, limit, offset)
        return [StkPremarketData(**row) for row in rows]
    
    async def list_premarket_by_stock(self, ts_code: str, start_date: Optional[datetime.date] = None, 
                                   end_date: Optional[datetime.date] = None, limit: int = 100) -> List[StkPremarketData]:
        """
        List premarket data for a specific stock within a date range.
        
        Args:
            ts_code (str): The TS code of the stock
            start_date (datetime.date, optional): Start date of the range
            end_date (datetime.date, optional): End date of the range
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[StkPremarketData]: List of premarket data
        """
        params = [ts_code]
        query = "SELECT * FROM stk_premarket WHERE ts_code = $1"
        
        if start_date:
            params.append(start_date)
            query += f" AND trade_date >= ${len(params)}"
            
        if end_date:
            params.append(end_date)
            query += f" AND trade_date <= ${len(params)}"
            
        query += " ORDER BY trade_date DESC LIMIT $" + str(len(params) + 1)
        params.append(limit)
        
        rows = await self.db.fetch(query, *params)
        return [StkPremarketData(**row) for row in rows]
    
    async def get_latest_premarket(self, ts_code: str) -> Optional[StkPremarketData]:
        """
        Get the latest premarket data for a stock.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            StkPremarketData | None: The latest premarket data if found, None otherwise
        """
        query = """
            SELECT * FROM stk_premarket 
            WHERE ts_code = $1
            ORDER BY trade_date DESC 
            LIMIT 1
        """
        row = await self.db.fetchrow(query, ts_code)
        return StkPremarketData(**row) if row else None