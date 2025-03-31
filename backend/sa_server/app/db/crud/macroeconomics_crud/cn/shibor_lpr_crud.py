import datetime
from typing import List, Optional, Tuple
from app.data.db_modules.macroeconomics_modules.cn.shibor_lpr import ShiborLprData


class ShiborLprCRUD:
    """
    CRUD operations for SHIBOR LPR (Loan Prime Rate) data.
    
    Provides methods to create, read, update, and delete SHIBOR LPR records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_lpr(self, data: ShiborLprData) -> None:
        """
        Create a new SHIBOR LPR record in the database.
        
        Args:
            data (ShiborLprData): The SHIBOR LPR data to insert
        """
        query = """
            INSERT INTO shibor_lpr (date, y1, y5)
            VALUES ($1, $2, $3)
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_lpr_by_date(self, date: datetime.date) -> Optional[ShiborLprData]:
        """
        Retrieve a SHIBOR LPR record by date.
        
        Args:
            date (datetime.date): The date of the LPR to retrieve
            
        Returns:
            ShiborLprData | None: The SHIBOR LPR data if found, None otherwise
        """
        query = "SELECT * FROM shibor_lpr WHERE date = $1"
        row = await self.db.fetchrow(query, date)
        return ShiborLprData(**row) if row else None
    
    async def get_lpr_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[ShiborLprData]:
        """
        Retrieve SHIBOR LPR records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[ShiborLprData]: List of SHIBOR LPR data for the date range
        """
        query = """
            SELECT * FROM shibor_lpr 
            WHERE date BETWEEN $1 AND $2
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [ShiborLprData(**row) for row in rows]
    
    async def update_lpr(self, date: datetime.date, updates: dict) -> None:
        """
        Update a SHIBOR LPR record by date.
        
        Args:
            date (datetime.date): The date of the LPR to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE shibor_lpr
            SET {set_values}
            WHERE date = $1
        """
        await self.db.execute(query, date, *updates.values())
    
    async def delete_lpr(self, date: datetime.date) -> None:
        """
        Delete a SHIBOR LPR record by date.
        
        Args:
            date (datetime.date): The date of the LPR to delete
        """
        query = "DELETE FROM shibor_lpr WHERE date = $1"
        await self.db.execute(query, date)
    
    async def delete_lpr_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Delete SHIBOR LPR records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM shibor_lpr WHERE date BETWEEN $1 AND $2"
        result = await self.db.execute(query, start_date, end_date)
        # 解析结果，格式类似 "DELETE 10"
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def list_lpr(self, limit: int = 100, offset: int = 0) -> List[ShiborLprData]:
        """
        List SHIBOR LPR records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[ShiborLprData]: List of SHIBOR LPR data
        """
        query = "SELECT * FROM shibor_lpr ORDER BY date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [ShiborLprData(**row) for row in rows]
    
    async def get_date_range(self) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Get the earliest and latest dates in the SHIBOR LPR records.
        
        Returns:
            Tuple[datetime.date, datetime.date]: Tuple of (earliest_date, latest_date)
        """
        query = """
            SELECT 
                MIN(date) AS earliest_date,
                MAX(date) AS latest_date
            FROM shibor_lpr
        """
        row = await self.db.fetchrow(query)
        return (row['earliest_date'], row['latest_date']) if row else (None, None)
    
    async def get_latest_lpr(self) -> Optional[ShiborLprData]:
        """
        Get the latest SHIBOR LPR record.
        
        Returns:
            ShiborLprData | None: The latest SHIBOR LPR data if available, None otherwise
        """
        query = "SELECT * FROM shibor_lpr ORDER BY date DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return ShiborLprData(**row) if row else None
    
    async def get_count(self) -> int:
        """
        Get the total count of SHIBOR LPR records.
        
        Returns:
            int: Count of records
        """
        query = "SELECT COUNT(*) FROM shibor_lpr"
        result = await self.db.fetchval(query)
        return result