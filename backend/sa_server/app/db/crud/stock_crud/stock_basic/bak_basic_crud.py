import datetime
from typing import List, Optional, Tuple
from app.data.db_modules.stock_modules.stock_basic.bak_basic import StockBakBasicData


class StockBakBasicCRUD:
    """
    CRUD operations for historical daily stock data.
    
    Provides methods to create, read, update, and delete bak_basic records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_bak_basic(self, data: StockBakBasicData) -> Tuple[str, datetime.date]:
        """
        Create a new historical stock record in the database.
        
        Args:
            data (StockBakBasicData): The historical stock data to insert
            
        Returns:
            Tuple[str, datetime.date]: The (ts_code, trade_date) composite key of the created record
        """
        query = """
            INSERT INTO bak_basic (
                trade_date, ts_code, name, industry, area, pe, float_share,
                total_share, total_assets, liquid_assets, fixed_assets,
                reserved, reserved_pershare, eps, bvps, pb, list_date,
                undp, per_undp, rev_yoy, profit_yoy, gpr, npr, holder_num
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24
            ) RETURNING ts_code, trade_date
        """
        data_dict = data.model_dump()
        values = list(data_dict.values())
        
        row = await self.db.fetchrow(query, *values)
        return row['ts_code'], row['trade_date']

    async def get_bak_basic(self, ts_code: str, trade_date: str) -> Optional[StockBakBasicData]:
        """
        Retrieve a historical stock record by its composite key.
        
        Args:
            ts_code (str): The TS code of the stock
            trade_date (str): The trading date (format: YYYY-MM-DD)
            
        Returns:
            Optional[StockBakBasicData]: The historical stock data if found, None otherwise
        """
        query = """
            SELECT * FROM bak_basic 
            WHERE ts_code = $1 AND trade_date = $2
        """
        row = await self.db.fetchrow(query, ts_code, trade_date)
        return StockBakBasicData(**row) if row else None
    
    async def get_bak_basic_by_stock(self, ts_code: str, limit: int = 100) -> List[StockBakBasicData]:
        """
        Retrieve historical records for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[StockBakBasicData]: List of historical stock data
        """
        query = """
            SELECT * FROM bak_basic 
            WHERE ts_code = $1
            ORDER BY trade_date DESC
            LIMIT $2
        """
        rows = await self.db.fetch(query, ts_code, limit)
        return [StockBakBasicData(**row) for row in rows]
    
    async def get_bak_basic_by_date(self, trade_date: str, limit: int = 1000) -> List[StockBakBasicData]:
        """
        Retrieve historical records for a specific trading date.
        
        Args:
            trade_date (str): The trading date (format: YYYY-MM-DD)
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[StockBakBasicData]: List of historical stock data
        """
        query = """
            SELECT * FROM bak_basic 
            WHERE trade_date = $1
            ORDER BY ts_code
            LIMIT $2
        """
        rows = await self.db.fetch(query, trade_date, limit)
        return [StockBakBasicData(**row) for row in rows]
    
    async def update_bak_basic(self, ts_code: str, trade_date: str, updates: dict) -> bool:
        """
        Update a historical stock record by its composite key.
        
        Args:
            ts_code (str): The TS code of the stock
            trade_date (str): The trading date (format: YYYY-MM-DD)
            updates (dict): Dictionary of fields to update and their new values
            
        Returns:
            bool: True if the record was updated, False otherwise
        """
        set_values = ','.join([f"{key} = ${idx + 3}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE bak_basic
            SET {set_values}
            WHERE ts_code = $1 AND trade_date = $2
        """
        result = await self.db.execute(query, ts_code, trade_date, *updates.values())
        
        # Parse result to determine if a record was updated
        try:
            parts = result.split()
            affected = int(parts[1]) if len(parts) >= 2 else 0
            return affected > 0
        except (IndexError, ValueError):
            return False
    
    async def delete_bak_basic(self, ts_code: str, trade_date: str) -> bool:
        """
        Delete a historical stock record by its composite key.
        
        Args:
            ts_code (str): The TS code of the stock
            trade_date (str): The trading date (format: YYYY-MM-DD)
            
        Returns:
            bool: True if the record was deleted, False otherwise
        """
        query = """
            DELETE FROM bak_basic 
            WHERE ts_code = $1 AND trade_date = $2
        """
        result = await self.db.execute(query, ts_code, trade_date)
        
        # Parse result to determine if a record was deleted
        try:
            parts = result.split()
            affected = int(parts[1]) if len(parts) >= 2 else 0
            return affected > 0
        except (IndexError, ValueError):
            return False
    
    async def delete_bak_basic_by_stock(self, ts_code: str) -> int:
        """
        Delete all historical records for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM bak_basic WHERE ts_code = $1"
        result = await self.db.execute(query, ts_code)
        
        # Parse result to get number of deleted records
        try:
            parts = result.split()
            return int(parts[1]) if len(parts) >= 2 else 0
        except (IndexError, ValueError):
            return 0
    
    async def delete_bak_basic_by_date(self, trade_date: str) -> int:
        """
        Delete all historical records for a specific trading date.
        
        Args:
            trade_date (str): The trading date (format: YYYY-MM-DD)
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM bak_basic WHERE trade_date = $1"
        result = await self.db.execute(query, trade_date)
        
        # Parse result to get number of deleted records
        try:
            parts = result.split()
            return int(parts[1]) if len(parts) >= 2 else 0
        except (IndexError, ValueError):
            return 0
    
    async def list_bak_basic(self, limit: int = 1000, offset: int = 0) -> List[StockBakBasicData]:
        """
        List historical stock records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[StockBakBasicData]: List of historical stock data
        """
        query = """
            SELECT * FROM bak_basic 
            ORDER BY trade_date DESC, ts_code 
            LIMIT $1 OFFSET $2
        """
        rows = await self.db.fetch(query, limit, offset)
        return [StockBakBasicData(**row) for row in rows]
    
    async def get_bak_basic_by_period(self, ts_code: str, start_date: str, end_date: str) -> List[StockBakBasicData]:
        """
        Retrieve historical records for a specific stock within a date range.
        
        Args:
            ts_code (str): The TS code of the stock
            start_date (str): Start date of the period (format: YYYY-MM-DD)
            end_date (str): End date of the period (format: YYYY-MM-DD)
            
        Returns:
            List[StockBakBasicData]: List of historical stock data in the period
        """
        query = """
            SELECT * FROM bak_basic 
            WHERE ts_code = $1 AND trade_date BETWEEN $2 AND $3
            ORDER BY trade_date
        """
        rows = await self.db.fetch(query, ts_code, start_date, end_date)
        return [StockBakBasicData(**row) for row in rows]
    
    async def get_industry_stocks(self, industry: str, trade_date: str) -> List[StockBakBasicData]:
        """
        Retrieve stocks in a specific industry on a specific date.
        
        Args:
            industry (str): The industry name
            trade_date (str): The trading date (format: YYYY-MM-DD)
            
        Returns:
            List[StockBakBasicData]: List of stock data in the industry
        """
        query = """
            SELECT * FROM bak_basic 
            WHERE industry = $1 AND trade_date = $2
            ORDER BY ts_code
        """
        rows = await self.db.fetch(query, industry, trade_date)
        return [StockBakBasicData(**row) for row in rows]
    
    async def get_area_stocks(self, area: str, trade_date: str) -> List[StockBakBasicData]:
        """
        Retrieve stocks in a specific area on a specific date.
        
        Args:
            area (str): The area name
            trade_date (str): The trading date (format: YYYY-MM-DD)
            
        Returns:
            List[StockBakBasicData]: List of stock data in the area
        """
        query = """
            SELECT * FROM bak_basic 
            WHERE area = $1 AND trade_date = $2
            ORDER BY ts_code
        """
        rows = await self.db.fetch(query, area, trade_date)
        return [StockBakBasicData(**row) for row in rows]
    
    async def get_industry_list(self, trade_date: str) -> List[str]:
        """
        Get list of all industries on a specific date.
        
        Args:
            trade_date (str): The trading date (format: YYYY-MM-DD)
            
        Returns:
            List[str]: List of industry names
        """
        query = """
            SELECT DISTINCT industry FROM bak_basic 
            WHERE trade_date = $1 AND industry IS NOT NULL
            ORDER BY industry
        """
        rows = await self.db.fetch(query, trade_date)
        return [row['industry'] for row in rows]
    
    async def get_area_list(self, trade_date: str) -> List[str]:
        """
        Get list of all areas on a specific date.
        
        Args:
            trade_date (str): The trading date (format: YYYY-MM-DD)
            
        Returns:
            List[str]: List of area names
        """
        query = """
            SELECT DISTINCT area FROM bak_basic 
            WHERE trade_date = $1 AND area IS NOT NULL
            ORDER BY area
        """
        rows = await self.db.fetch(query, trade_date)
        return [row['area'] for row in rows]