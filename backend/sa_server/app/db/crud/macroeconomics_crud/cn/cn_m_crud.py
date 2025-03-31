from typing import List, Optional
from app.data.db_modules.macroeconomics_modules.cn.cn_m import CnMData


class CnMCRUD:
    """
    CRUD operations for China monetary supply data.
    
    Provides methods to create, read, update, and delete monetary supply records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_m(self, data: CnMData) -> None:
        """
        Create a new monetary supply record in the database.
        
        Args:
            data (CnMData): The monetary supply data to insert
        """
        query = """
            INSERT INTO cn_m (
                month, m0, m0_yoy, m0_mom,
                m1, m1_yoy, m1_mom,
                m2, m2_yoy, m2_mom
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_m_by_month(self, month: str) -> Optional[CnMData]:
        """
        Retrieve a monetary supply record by its month.
        
        Args:
            month (str): The month of the monetary supply record to retrieve (e.g., '202301')
            
        Returns:
            CnMData | None: The monetary supply data if found, None otherwise
        """
        query = "SELECT * FROM cn_m WHERE month = $1"
        row = await self.db.fetchrow(query, month)
        return CnMData(**row) if row else None
    
    async def update_m(self, month: str, updates: dict) -> None:
        """
        Update a monetary supply record by its month.
        
        Args:
            month (str): The month of the monetary supply record to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE cn_m
            SET {set_values}
            WHERE month = $1
        """
        await self.db.execute(query, month, *updates.values())
    
    async def delete_m(self, month: str) -> None:
        """
        Delete a monetary supply record by its month.
        
        Args:
            month (str): The month of the monetary supply record to delete
        """
        query = "DELETE FROM cn_m WHERE month = $1"
        await self.db.execute(query, month)
    
    async def list_m(self, limit: int = 20, offset: int = 0) -> List[CnMData]:
        """
        List monetary supply records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[CnMData]: List of monetary supply data
        """
        query = "SELECT * FROM cn_m ORDER BY month DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [CnMData(**row) for row in rows]
    
    async def get_m_range(self, start_month: str, end_month: str) -> List[CnMData]:
        """
        Retrieve monetary supply records within a month range.
        
        Args:
            start_month (str): The start month (inclusive)
            end_month (str): The end month (inclusive)
            
        Returns:
            list[CnMData]: List of monetary supply data within the month range
        """
        query = """
            SELECT * FROM cn_m 
            WHERE month >= $1 AND month <= $2
            ORDER BY month
        """
        rows = await self.db.fetch(query, start_month, end_month)
        return [CnMData(**row) for row in rows]
    
    async def get_latest_m(self) -> Optional[CnMData]:
        """
        Retrieve the most recent monetary supply record.
        
        Returns:
            CnMData | None: The most recent monetary supply data if found, None otherwise
        """
        query = "SELECT * FROM cn_m ORDER BY month DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return CnMData(**row) if row else None
    
    async def get_year_m(self, year: int) -> List[CnMData]:
        """
        Retrieve all monetary supply records for a specific year.
        
        Args:
            year (int): The year to retrieve data for
            
        Returns:
            list[CnMData]: List of monetary supply data for the specified year
        """
        start_month = f"{year}01"
        end_month = f"{year}12"
        
        query = """
            SELECT * FROM cn_m 
            WHERE month >= $1 AND month <= $2
            ORDER BY month
        """
        rows = await self.db.fetch(query, start_month, end_month)
        return [CnMData(**row) for row in rows]
    
    async def get_m_growth_trend(self, months: int = 12) -> List[dict]:
        """
        Retrieve monetary supply growth trend for recent months.
        
        Args:
            months (int): Number of months to look back
            
        Returns:
            list[dict]: List of months and their monetary supply growth rates
        """
        query = """
            SELECT month, m0_yoy, m1_yoy, m2_yoy
            FROM cn_m 
            ORDER BY month DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, months)
        
        # Sort by month in ascending order for trend analysis
        result = [{
            "month": row["month"], 
            "m0_yoy": row["m0_yoy"], 
            "m1_yoy": row["m1_yoy"], 
            "m2_yoy": row["m2_yoy"]
        } for row in rows]
        
        return sorted(result, key=lambda x: x["month"])
    
    async def get_m_levels(self, months: int = 12) -> List[dict]:
        """
        Retrieve monetary supply levels for recent months.
        
        Args:
            months (int): Number of months to look back
            
        Returns:
            list[dict]: List of months and their monetary supply levels
        """
        query = """
            SELECT month, m0, m1, m2
            FROM cn_m 
            ORDER BY month DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, months)
        
        # Sort by month in ascending order
        result = [{
            "month": row["month"], 
            "m0": row["m0"], 
            "m1": row["m1"], 
            "m2": row["m2"]
        } for row in rows]
        
        return sorted(result, key=lambda x: x["month"])

    async def get_all_m(self) -> List[CnMData]:
        """
        Retrieve all monetary supply records from the table.
        
        Returns:
            list[CnMData]: Complete list of monetary supply data
        """
        query = "SELECT * FROM cn_m ORDER BY month"
        rows = await self.db.fetch(query)
        return [CnMData(**row) for row in rows]