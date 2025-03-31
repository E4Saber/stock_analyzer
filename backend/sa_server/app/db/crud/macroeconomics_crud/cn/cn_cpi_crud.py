from typing import List, Optional
from app.utils.json_utils import clean_nan_response
from app.data.db_modules.macroeconomics_modules.cn.cn_cpi import CnCpiData


class CnCpiCRUD:
    """
    CRUD operations for China CPI data.
    
    Provides methods to create, read, update, and delete CPI records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_cpi(self, data: CnCpiData) -> None:
        """
        Create a new CPI record in the database.
        
        Args:
            data (CnCpiData): The CPI data to insert
        """
        query = """
            INSERT INTO cn_cpi (
                month, nt_val, nt_yoy, nt_mom, nt_accu, 
                town_val, town_yoy, town_mom, town_accu,
                cnt_val, cnt_yoy, cnt_mom, cnt_accu
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_cpi_by_month(self, month: str) -> Optional[CnCpiData]:
        """
        Retrieve a CPI record by its month.
        
        Args:
            month (str): The month of the CPI record to retrieve (e.g., '202301')
            
        Returns:
            CnCpiData | None: The CPI data if found, None otherwise
        """
        query = "SELECT * FROM cn_cpi WHERE month = $1"
        row = await self.db.fetchrow(query, month)
        return CnCpiData(**row) if row else None
    
    async def update_cpi(self, month: str, updates: dict) -> None:
        """
        Update a CPI record by its month.
        
        Args:
            month (str): The month of the CPI record to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE cn_cpi
            SET {set_values}
            WHERE month = $1
        """
        await self.db.execute(query, month, *updates.values())
    
    async def delete_cpi(self, month: str) -> None:
        """
        Delete a CPI record by its month.
        
        Args:
            month (str): The month of the CPI record to delete
        """
        query = "DELETE FROM cn_cpi WHERE month = $1"
        await self.db.execute(query, month)
    
    async def list_cpi(self, limit: int = 20, offset: int = 0) -> List[CnCpiData]:
        """
        List CPI records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[CnCpiData]: List of CPI data
        """
        query = "SELECT * FROM cn_cpi ORDER BY month DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [CnCpiData(**row) for row in rows]
    
    async def get_cpi_range(self, start_month: str, end_month: str) -> List[CnCpiData]:
        """
        Retrieve CPI records within a month range.
        
        Args:
            start_month (str): The start month (inclusive)
            end_month (str): The end month (inclusive)
            
        Returns:
            list[CnCpiData]: List of CPI data within the month range
        """
        query = """
            SELECT * FROM cn_cpi 
            WHERE month >= $1 AND month <= $2
            ORDER BY month
        """
        rows = await self.db.fetch(query, start_month, end_month)
        return [CnCpiData(**row) for row in rows]
    
    async def get_latest_cpi(self) -> Optional[CnCpiData]:
        """
        Retrieve the most recent CPI record.
        
        Returns:
            CnCpiData | None: The most recent CPI data if found, None otherwise
        """
        query = "SELECT * FROM cn_cpi ORDER BY month DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return CnCpiData(**row) if row else None
    
    async def get_year_cpi(self, year: int) -> List[CnCpiData]:
        """
        Retrieve all CPI records for a specific year.
        
        Args:
            year (int): The year to retrieve data for
            
        Returns:
            list[CnCpiData]: List of CPI data for the specified year
        """
        start_month = f"{year}01"
        end_month = f"{year}12"
        
        query = """
            SELECT * FROM cn_cpi 
            WHERE month >= $1 AND month <= $2
            ORDER BY month
        """
        rows = await self.db.fetch(query, start_month, end_month)
        return [CnCpiData(**row) for row in rows]
    
    async def get_cpi_trend(self, months: int = 12) -> List[dict]:
        """
        Retrieve CPI trend for recent months.
        
        Args:
            months (int): Number of months to look back
            
        Returns:
            list[dict]: List of months and their CPI values and growth rates
        """
        query = """
            SELECT month, nt_val, nt_yoy, nt_mom
            FROM cn_cpi 
            ORDER BY month DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, months)
        
        # Sort by month in ascending order for trend analysis
        result = [{"month": row["month"], "nt_val": row["nt_val"], "nt_yoy": row["nt_yoy"], "nt_mom": row["nt_mom"]} for row in rows]
        return sorted(result, key=lambda x: x["month"])

    @clean_nan_response
    async def get_all_cpi(self) -> List[CnCpiData]:
        """
        Retrieve all CPI records from the table.
        
        Returns:
            list[CnCpiData]: Complete list of CPI data
        """
        query = "SELECT * FROM cn_cpi ORDER BY month"
        rows = await self.db.fetch(query)
        return [CnCpiData(**row) for row in rows]