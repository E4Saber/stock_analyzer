import datetime
from typing import List, Optional
from app.data.db_modules.stock_modules.stock_basic.namechange import NameChangeData


class NameChangeCRUD:
    """
    CRUD operations for stock name change data.
    
    Provides methods to create, read, update, and delete stock name change records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_namechange(self, data: NameChangeData) -> int:
        """
        Create a new stock name change record in the database.
        
        Args:
            data (NameChangeData): The name change data to insert
            
        Returns:
            int: The ID of the newly created record
        """
        query = """
            INSERT INTO namechange (
                ts_code, name, start_date, end_date, ann_date, change_reason
            ) VALUES (
                $1, $2, $3, $4, $5, $6
            ) RETURNING id
        """
        values = [
            data.ts_code,
            data.name,
            data.start_date,
            data.end_date,
            data.ann_date,
            data.change_reason
        ]
        return await self.db.fetchval(query, *values)

    async def get_namechange_by_id(self, id: int) -> Optional[NameChangeData]:
        """
        Retrieve a stock name change record by its ID.
        
        Args:
            id (int): The record ID to retrieve
            
        Returns:
            NameChangeData | None: The name change data if found, None otherwise
        """
        query = "SELECT * FROM namechange WHERE id = $1"
        row = await self.db.fetchrow(query, id)
        return NameChangeData(**row) if row else None
    
    async def get_namechange_by_ts_code_and_date(self, ts_code: str, start_date: datetime.date) -> Optional[NameChangeData]:
        """
        Retrieve a stock name change record by its TS code and start date.
        
        Args:
            ts_code (str): The TS code of the stock
            start_date (datetime.date): The start date of the name change
            
        Returns:
            NameChangeData | None: The name change data if found, None otherwise
        """
        query = "SELECT * FROM namechange WHERE ts_code = $1 AND start_date = $2"
        row = await self.db.fetchrow(query, ts_code, start_date)
        return NameChangeData(**row) if row else None
    
    async def get_namechange_by_date(self, date: datetime.date) -> List[NameChangeData]:
        """
        Retrieve all stock name changes that were in effect on a specific date.
        
        Args:
            date (datetime.date): The date to check
            
        Returns:
            List[NameChangeData]: List of name changes
        """
        query = """
            SELECT * FROM namechange 
            WHERE start_date <= $1 AND (end_date IS NULL OR end_date >= $1)
            ORDER BY ts_code
        """
        rows = await self.db.fetch(query, date)
        return [NameChangeData(**row) for row in rows]
    
    async def update_namechange(self, id: int, updates: dict) -> bool:
        """
        Update a stock name change record by its ID.
        
        Args:
            id (int): The ID of the record to update
            updates (dict): Dictionary of fields to update and their new values
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE namechange
            SET {set_values}
            WHERE id = $1
        """
        result = await self.db.execute(query, id, *updates.values())
        return 'UPDATE' in result
    
    async def delete_namechange(self, id: int) -> bool:
        """
        Delete a stock name change record by its ID.
        
        Args:
            id (int): The ID of the record to delete
            
        Returns:
            bool: True if the deletion was successful, False otherwise
        """
        query = "DELETE FROM namechange WHERE id = $1"
        result = await self.db.execute(query, id)
        return 'DELETE' in result
    
    async def list_namechanges_by_ts_code(self, ts_code: str) -> List[NameChangeData]:
        """
        List all name changes for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            List[NameChangeData]: List of name changes
        """
        query = """
            SELECT * FROM namechange 
            WHERE ts_code = $1
            ORDER BY start_date DESC
        """
        rows = await self.db.fetch(query, ts_code)
        return [NameChangeData(**row) for row in rows]
    
    async def find_namechanges_by_name(self, name_pattern: str, limit: int = 100) -> List[NameChangeData]:
        """
        Find name changes by matching part of the name.
        
        Args:
            name_pattern (str): The pattern to match in the name
            limit (int): Maximum number of records to return
            
        Returns:
            List[NameChangeData]: List of matching name changes
        """
        query = """
            SELECT * FROM namechange 
            WHERE name ILIKE $1
            ORDER BY start_date DESC
            LIMIT $2
        """
        pattern = f"%{name_pattern}%"
        rows = await self.db.fetch(query, pattern, limit)
        return [NameChangeData(**row) for row in rows]
    
    async def get_current_name(self, ts_code: str, date: Optional[datetime.date] = None) -> Optional[str]:
        """
        Get the current or historical name of a stock at a specific date.
        
        Args:
            ts_code (str): The TS code of the stock
            date (datetime.date, optional): The date to check, defaults to current date
            
        Returns:
            str | None: The stock name if found, None otherwise
        """
        check_date = date or datetime.date.today()
        
        query = """
            SELECT name FROM namechange 
            WHERE ts_code = $1 AND start_date <= $2 AND (end_date IS NULL OR end_date >= $2)
            ORDER BY start_date DESC
            LIMIT 1
        """
        return await self.db.fetchval(query, ts_code, check_date)