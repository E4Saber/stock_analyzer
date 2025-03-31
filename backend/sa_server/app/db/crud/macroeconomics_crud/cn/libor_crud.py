import datetime
from typing import List, Optional, Tuple
from app.data.db_modules.macroeconomics_modules.cn.libor import LiborData


class LiborCRUD:
    """
    CRUD operations for LIBOR (London Interbank Offered Rate) data.
    
    Provides methods to create, read, update, and delete LIBOR records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_libor(self, data: LiborData) -> None:
        """
        Create a new LIBOR record in the database.
        
        Args:
            data (LiborData): The LIBOR data to insert
        """
        query = """
            INSERT INTO libor (
                date, curr_type, on_rate, w1_rate, m1_rate, m2_rate, 
                m3_rate, m6_rate, m12_rate
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_libor_by_date_currency(self, date: datetime.date, curr_type: str) -> Optional[LiborData]:
        """
        Retrieve a LIBOR record by date and currency type.
        
        Args:
            date (datetime.date): The date of the LIBOR to retrieve
            curr_type (str): The currency type
            
        Returns:
            LiborData | None: The LIBOR data if found, None otherwise
        """
        query = "SELECT * FROM libor WHERE date = $1 AND curr_type = $2"
        row = await self.db.fetchrow(query, date, curr_type)
        return LiborData(**row) if row else None
    
    async def get_libor_by_date(self, date: datetime.date) -> List[LiborData]:
        """
        Retrieve all LIBOR records for a specific date.
        
        Args:
            date (datetime.date): The date to retrieve LIBOR for
            
        Returns:
            List[LiborData]: List of LIBOR data for the date
        """
        query = "SELECT * FROM libor WHERE date = $1 ORDER BY curr_type"
        rows = await self.db.fetch(query, date)
        return [LiborData(**row) for row in rows]
    
    async def get_libor_by_currency(self, curr_type: str, limit: int = 100, offset: int = 0) -> List[LiborData]:
        """
        Retrieve LIBOR records for a specific currency with pagination.
        
        Args:
            curr_type (str): The currency type
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[LiborData]: List of LIBOR data for the currency
        """
        query = "SELECT * FROM libor WHERE curr_type = $1 ORDER BY date DESC LIMIT $2 OFFSET $3"
        rows = await self.db.fetch(query, curr_type, limit, offset)
        return [LiborData(**row) for row in rows]
    
    async def get_libor_by_date_range(self, start_date: datetime.date, end_date: datetime.date, 
                                     curr_type: Optional[str] = None) -> List[LiborData]:
        """
        Retrieve LIBOR records for a date range and optionally for a specific currency.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            curr_type (str, optional): Currency type to filter by
            
        Returns:
            List[LiborData]: List of LIBOR data for the date range
        """
        if curr_type:
            query = """
                SELECT * FROM libor 
                WHERE date BETWEEN $1 AND $2 AND curr_type = $3
                ORDER BY date DESC, curr_type
            """
            rows = await self.db.fetch(query, start_date, end_date, curr_type)
        else:
            query = """
                SELECT * FROM libor 
                WHERE date BETWEEN $1 AND $2
                ORDER BY date DESC, curr_type
            """
            rows = await self.db.fetch(query, start_date, end_date)
        
        return [LiborData(**row) for row in rows]
    
    async def update_libor(self, date: datetime.date, curr_type: str, updates: dict) -> None:
        """
        Update a LIBOR record by date and currency type.
        
        Args:
            date (datetime.date): The date of the LIBOR to update
            curr_type (str): The currency type
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 3}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE libor
            SET {set_values}
            WHERE date = $1 AND curr_type = $2
        """
        await self.db.execute(query, date, curr_type, *updates.values())
    
    async def delete_libor(self, date: datetime.date, curr_type: str) -> None:
        """
        Delete a LIBOR record by date and currency type.
        
        Args:
            date (datetime.date): The date of the LIBOR to delete
            curr_type (str): The currency type
        """
        query = "DELETE FROM libor WHERE date = $1 AND curr_type = $2"
        await self.db.execute(query, date, curr_type)
    
    async def delete_libor_by_date(self, date: datetime.date) -> int:
        """
        Delete all LIBOR records for a specific date.
        
        Args:
            date (datetime.date): The date to delete LIBOR for
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM libor WHERE date = $1"
        result = await self.db.execute(query, date)
        # 解析结果，格式类似 "DELETE 10"
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def delete_libor_by_currency(self, curr_type: str) -> int:
        """
        Delete all LIBOR records for a specific currency.
        
        Args:
            curr_type (str): The currency type
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM libor WHERE curr_type = $1"
        result = await self.db.execute(query, curr_type)
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def list_libor(self, limit: int = 100, offset: int = 0) -> List[LiborData]:
        """
        List LIBOR records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[LiborData]: List of LIBOR data
        """
        query = "SELECT * FROM libor ORDER BY date DESC, curr_type LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [LiborData(**row) for row in rows]
    
    async def get_date_range(self, curr_type: Optional[str] = None) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Get the earliest and latest dates in the LIBOR records.
        
        Args:
            curr_type (str, optional): Currency type to filter by
            
        Returns:
            Tuple[datetime.date, datetime.date]: Tuple of (earliest_date, latest_date)
        """
        if curr_type:
            query = """
                SELECT 
                    MIN(date) AS earliest_date,
                    MAX(date) AS latest_date
                FROM libor
                WHERE curr_type = $1
            """
            row = await self.db.fetchrow(query, curr_type)
        else:
            query = """
                SELECT 
                    MIN(date) AS earliest_date,
                    MAX(date) AS latest_date
                FROM libor
            """
            row = await self.db.fetchrow(query)
        
        return (row['earliest_date'], row['latest_date']) if row else (None, None)
    
    async def get_currency_types(self) -> List[str]:
        """
        Get a list of all currency types in the LIBOR records.
        
        Returns:
            List[str]: List of currency types
        """
        query = "SELECT DISTINCT curr_type FROM libor ORDER BY curr_type"
        rows = await self.db.fetch(query)
        return [row['curr_type'] for row in rows]
    
    async def get_latest_libor_by_currency(self, curr_type: str) -> Optional[LiborData]:
        """
        Get the latest LIBOR record for a specific currency.
        
        Args:
            curr_type (str): The currency type
            
        Returns:
            LiborData | None: The latest LIBOR data if available, None otherwise
        """
        query = "SELECT * FROM libor WHERE curr_type = $1 ORDER BY date DESC LIMIT 1"
        row = await self.db.fetchrow(query, curr_type)
        return LiborData(**row) if row else None