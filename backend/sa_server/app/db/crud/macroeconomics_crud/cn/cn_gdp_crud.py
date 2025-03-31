from typing import List, Optional
from app.data.db_modules.macroeconomics_modules.cn.cn_gdp import CnGdpData


class CnGdpCRUD:
    """
    CRUD operations for China GDP data.
    
    Provides methods to create, read, update, and delete GDP records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_gdp(self, data: CnGdpData) -> None:
        """
        Create a new GDP record in the database.
        
        Args:
            data (CnGdpData): The GDP data to insert
        """
        query = """
            INSERT INTO cn_gdp (
                quarter, gdp, gdp_yoy, pi, pi_yoy, 
                si, si_yoy, ti, ti_yoy
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_gdp_by_quarter(self, quarter: str) -> Optional[CnGdpData]:
        """
        Retrieve a GDP record by its quarter.
        
        Args:
            quarter (str): The quarter of the GDP record to retrieve (e.g., '2023Q1')
            
        Returns:
            CnGdpData | None: The GDP data if found, None otherwise
        """
        query = "SELECT * FROM cn_gdp WHERE quarter = $1"
        row = await self.db.fetchrow(query, quarter)
        return CnGdpData(**row) if row else None
    
    async def update_gdp(self, quarter: str, updates: dict) -> None:
        """
        Update a GDP record by its quarter.
        
        Args:
            quarter (str): The quarter of the GDP record to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE cn_gdp
            SET {set_values}
            WHERE quarter = $1
        """
        await self.db.execute(query, quarter, *updates.values())
    
    async def delete_gdp(self, quarter: str) -> None:
        """
        Delete a GDP record by its quarter.
        
        Args:
            quarter (str): The quarter of the GDP record to delete
        """
        query = "DELETE FROM cn_gdp WHERE quarter = $1"
        await self.db.execute(query, quarter)
    
    async def list_gdp(self, limit: int = 20, offset: int = 0) -> List[CnGdpData]:
        """
        List GDP records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[CnGdpData]: List of GDP data
        """
        query = "SELECT * FROM cn_gdp ORDER BY quarter DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [CnGdpData(**row) for row in rows]
    
    async def get_gdp_range(self, start_quarter: str, end_quarter: str) -> List[CnGdpData]:
        """
        Retrieve GDP records within a quarter range.
        
        Args:
            start_quarter (str): The start quarter (inclusive)
            end_quarter (str): The end quarter (inclusive)
            
        Returns:
            list[CnGdpData]: List of GDP data within the quarter range
        """
        query = """
            SELECT * FROM cn_gdp 
            WHERE quarter >= $1 AND quarter <= $2
            ORDER BY quarter
        """
        rows = await self.db.fetch(query, start_quarter, end_quarter)
        return [CnGdpData(**row) for row in rows]
    
    async def get_latest_gdp(self) -> Optional[CnGdpData]:
        """
        Retrieve the most recent GDP record.
        
        Returns:
            CnGdpData | None: The most recent GDP data if found, None otherwise
        """
        query = "SELECT * FROM cn_gdp ORDER BY quarter DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return CnGdpData(**row) if row else None
    
    async def get_year_gdp(self, year: int) -> List[CnGdpData]:
        """
        Retrieve all GDP records for a specific year.
        
        Args:
            year (int): The year to retrieve data for
            
        Returns:
            list[CnGdpData]: List of GDP data for the specified year
        """
        start_quarter = f"{year}Q1"
        end_quarter = f"{year}Q4"
        
        query = """
            SELECT * FROM cn_gdp 
            WHERE quarter >= $1 AND quarter <= $2
            ORDER BY quarter
        """
        rows = await self.db.fetch(query, start_quarter, end_quarter)
        return [CnGdpData(**row) for row in rows]
    
    async def get_gdp_growth_trend(self, years: int = 5) -> List[dict]:
        """
        Retrieve GDP growth trend for recent years.
        
        Args:
            years (int): Number of years to look back
            
        Returns:
            list[dict]: List of quarters and their GDP growth rates
        """
        query = """
            SELECT quarter, gdp_yoy
            FROM cn_gdp 
            ORDER BY quarter DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, years * 4)  # 4 quarters per year
        
        # Sort by quarter in ascending order for trend analysis
        result = [{"quarter": row["quarter"], "gdp_yoy": row["gdp_yoy"]} for row in rows]
        return sorted(result, key=lambda x: x["quarter"])

    async def get_all_gdp(self) -> List[CnGdpData]:
        """
        Retrieve all GDP records from the table.
        
        Returns:
            list[CnGdpData]: Complete list of GDP data
        """
        query = "SELECT * FROM cn_gdp ORDER BY quarter"
        rows = await self.db.fetch(query)
        return [CnGdpData(**row) for row in rows]