import datetime
from typing import List, Optional
from app.data.db_modules.stock_modules.stock_basic.hs_const import HsConstData


class HsConstCRUD:
    """
    CRUD operations for Hong Kong Stock Connect constituent stock data.
    
    Provides methods to create, read, update, and delete constituent stock records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_hs_const(self, data: HsConstData) -> int:
        """
        Create a new Hong Kong Stock Connect constituent stock record in the database.
        
        Args:
            data (HsConstData): The constituent stock data to insert
            
        Returns:
            int: The ID of the newly created record
        """
        query = """
            INSERT INTO hs_const (
                ts_code, hs_type, in_date, out_date, is_new
            ) VALUES (
                $1, $2, $3, $4, $5
            ) RETURNING id
        """
        values = [
            data.ts_code,
            data.hs_type,
            data.in_date,
            data.out_date,
            data.is_new
        ]
        return await self.db.fetchval(query, *values)

    async def get_hs_const_by_id(self, id: int) -> Optional[HsConstData]:
        """
        Retrieve a constituent stock record by its ID.
        
        Args:
            id (int): The record ID to retrieve
            
        Returns:
            HsConstData | None: The constituent stock data if found, None otherwise
        """
        query = "SELECT * FROM hs_const WHERE id = $1"
        row = await self.db.fetchrow(query, id)
        return HsConstData(**row) if row else None
    
    async def get_hs_const_by_key(self, ts_code: str, hs_type: str, in_date: datetime.date) -> Optional[HsConstData]:
        """
        Retrieve a constituent stock record by its unique key.
        
        Args:
            ts_code (str): The TS code of the stock
            hs_type (str): The Stock Connect type (SH/SZ)
            in_date (datetime.date): The inclusion date
            
        Returns:
            HsConstData | None: The constituent stock data if found, None otherwise
        """
        query = "SELECT * FROM hs_const WHERE ts_code = $1 AND hs_type = $2 AND in_date = $3"
        row = await self.db.fetchrow(query, ts_code, hs_type, in_date)
        return HsConstData(**row) if row else None
    
    async def update_hs_const(self, id: int, updates: dict) -> bool:
        """
        Update a constituent stock record by its ID.
        
        Args:
            id (int): The ID of the record to update
            updates (dict): Dictionary of fields to update and their new values
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE hs_const
            SET {set_values}
            WHERE id = $1
        """
        result = await self.db.execute(query, id, *updates.values())
        return 'UPDATE' in result
    
    async def delete_hs_const(self, id: int) -> bool:
        """
        Delete a constituent stock record by its ID.
        
        Args:
            id (int): The ID of the record to delete
            
        Returns:
            bool: True if the deletion was successful, False otherwise
        """
        query = "DELETE FROM hs_const WHERE id = $1"
        result = await self.db.execute(query, id)
        return 'DELETE' in result
    
    async def list_hs_const_by_stock(self, ts_code: str) -> List[HsConstData]:
        """
        List all constituent stock records for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            List[HsConstData]: List of constituent stock records
        """
        query = """
            SELECT * FROM hs_const 
            WHERE ts_code = $1
            ORDER BY in_date DESC
        """
        rows = await self.db.fetch(query, ts_code)
        return [HsConstData(**row) for row in rows]
    
    async def list_hs_const_by_type(self, hs_type: str, is_new: str = '1') -> List[HsConstData]:
        """
        List all constituent stocks for a specific Stock Connect type.
        
        Args:
            hs_type (str): The Stock Connect type (SH/SZ)
            is_new (str): Filter by is_new flag, defaults to '1' (latest records only)
            
        Returns:
            List[HsConstData]: List of constituent stock records
        """
        query = """
            SELECT * FROM hs_const 
            WHERE hs_type = $1 AND is_new = $2
            ORDER BY ts_code
        """
        rows = await self.db.fetch(query, hs_type, is_new)
        return [HsConstData(**row) for row in rows]
    
    async def get_current_constituents(self, hs_type: Optional[str] = None) -> List[HsConstData]:
        """
        Get all current constituent stocks.
        
        Args:
            hs_type (str, optional): Filter by Stock Connect type (SH/SZ), None for both
            
        Returns:
            List[HsConstData]: List of current constituent stock records
        """
        if hs_type:
            query = """
                SELECT * FROM hs_const 
                WHERE hs_type = $1 AND is_new = '1'
                ORDER BY ts_code
            """
            rows = await self.db.fetch(query, hs_type)
        else:
            query = """
                SELECT * FROM hs_const 
                WHERE is_new = '1'
                ORDER BY hs_type, ts_code
            """
            rows = await self.db.fetch(query)
        
        return [HsConstData(**row) for row in rows]
    
    async def check_is_constituent(self, ts_code: str, date: Optional[datetime.date] = None, hs_type: Optional[str] = None) -> bool:
        """
        Check if a stock is a constituent stock at a specific date.
        
        Args:
            ts_code (str): The TS code of the stock
            date (datetime.date, optional): The date to check, defaults to current date
            hs_type (str, optional): The Stock Connect type (SH/SZ), None for either
            
        Returns:
            bool: True if the stock is a constituent stock, False otherwise
        """
        check_date = date or datetime.date.today()
        
        if hs_type:
            query = """
                SELECT 1 FROM hs_const 
                WHERE ts_code = $1 AND hs_type = $2 AND in_date <= $3 
                AND (out_date IS NULL OR out_date >= $3)
                LIMIT 1
            """
            result = await self.db.fetchval(query, ts_code, hs_type, check_date)
        else:
            query = """
                SELECT 1 FROM hs_const 
                WHERE ts_code = $1 AND in_date <= $2 
                AND (out_date IS NULL OR out_date >= $2)
                LIMIT 1
            """
            result = await self.db.fetchval(query, ts_code, check_date)
        
        return result is not None