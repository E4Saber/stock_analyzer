from typing import List, Optional
from datetime import date, timedelta
from app.data.db_modules.macroeconomics_modules.cn.shibor import ShiborData


class ShiborCRUD:
    """
    CRUD operations for Shibor data.
    
    Provides methods to create, read, update, and delete Shibor records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_shibor(self, data: ShiborData) -> None:
        """
        Create a new Shibor record in the database.
        
        Args:
            data (ShiborData): The Shibor data to insert
        """
        query = """
            INSERT INTO shibor (
                date, on_rate, w1_rate, w2_rate, m1_rate, 
                m3_rate, m6_rate, m9_rate, y1_rate
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_shibor_by_date(self, date_value: date) -> Optional[ShiborData]:
        """
        Retrieve a Shibor record by its date.
        
        Args:
            date_value (date): The date of the Shibor record to retrieve
            
        Returns:
            ShiborData | None: The Shibor data if found, None otherwise
        """
        query = "SELECT * FROM shibor WHERE date = $1"
        row = await self.db.fetchrow(query, date_value)
        return ShiborData(**row) if row else None
    
    async def update_shibor(self, date_value: date, updates: dict) -> None:
        """
        Update a Shibor record by its date.
        
        Args:
            date_value (date): The date of the Shibor record to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE shibor
            SET {set_values}
            WHERE date = $1
        """
        await self.db.execute(query, date_value, *updates.values())
    
    async def delete_shibor(self, date_value: date) -> None:
        """
        Delete a Shibor record by its date.
        
        Args:
            date_value (date): The date of the Shibor record to delete
        """
        query = "DELETE FROM shibor WHERE date = $1"
        await self.db.execute(query, date_value)
    
    async def list_shibor(self, limit: int = 100, offset: int = 0) -> List[ShiborData]:
        """
        List Shibor records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[ShiborData]: List of Shibor data
        """
        query = "SELECT * FROM shibor ORDER BY date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [ShiborData(**row) for row in rows]
    
    async def get_shibor_range(self, start_date: date, end_date: date) -> List[ShiborData]:
        """
        Retrieve Shibor records within a date range.
        
        Args:
            start_date (date): The start date (inclusive)
            end_date (date): The end date (inclusive)
            
        Returns:
            list[ShiborData]: List of Shibor data within the date range
        """
        query = """
            SELECT * FROM shibor 
            WHERE date >= $1 AND date <= $2
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [ShiborData(**row) for row in rows]
    
    async def get_latest_shibor(self) -> Optional[ShiborData]:
        """
        Retrieve the most recent Shibor record.
        
        Returns:
            ShiborData | None: The most recent Shibor data if found, None otherwise
        """
        query = "SELECT * FROM shibor ORDER BY date DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return ShiborData(**row) if row else None
    
    async def get_historical_trend(self, rate_type: str, days: int = 30) -> List[dict]:
        """
        Retrieve historical trend data for a specific rate type.
        
        Args:
            rate_type (str): The rate type to retrieve (on_rate, w1_rate, etc.)
            days (int): Number of days to look back
            
        Returns:
            list[dict]: List of date and rate values
        """
        if rate_type not in ["on_rate", "w1_rate", "w2_rate", "m1_rate", 
                            "m3_rate", "m6_rate", "m9_rate", "y1_rate"]:
            raise ValueError(f"Invalid rate type: {rate_type}")
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        query = f"""
            SELECT date, {rate_type} as rate
            FROM shibor 
            WHERE date >= $1 AND date <= $2 AND {rate_type} IS NOT NULL
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [{"date": row["date"], "rate": row["rate"]} for row in rows]