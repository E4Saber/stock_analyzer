from typing import List, Optional
from app.data.db_modules.macroeconomics_modules.cn.cn_ppi import CnPpiData


class CnPpiCRUD:
    """
    CRUD operations for China PPI data.
    
    Provides methods to create, read, update, and delete PPI records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_ppi(self, data: CnPpiData) -> None:
        """
        Create a new PPI record in the database.
        
        Args:
            data (CnPpiData): The PPI data to insert
        """
        # 将Pydantic模型转换为字典
        data_dict = data.model_dump()
        
        # 构建SQL语句
        columns = ", ".join(data_dict.keys())
        placeholders = ", ".join(f"${i+1}" for i in range(len(data_dict)))
        
        query = f"""
            INSERT INTO cn_ppi ({columns})
            VALUES ({placeholders})
        """
        
        await self.db.execute(query, *data_dict.values())

    async def get_ppi_by_month(self, month: str) -> Optional[CnPpiData]:
        """
        Retrieve a PPI record by its month.
        
        Args:
            month (str): The month of the PPI record to retrieve (e.g., '202301')
            
        Returns:
            CnPpiData | None: The PPI data if found, None otherwise
        """
        query = "SELECT * FROM cn_ppi WHERE month = $1"
        row = await self.db.fetchrow(query, month)
        return CnPpiData(**row) if row else None
    
    async def update_ppi(self, month: str, updates: dict) -> None:
        """
        Update a PPI record by its month.
        
        Args:
            month (str): The month of the PPI record to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE cn_ppi
            SET {set_values}
            WHERE month = $1
        """
        await self.db.execute(query, month, *updates.values())
    
    async def delete_ppi(self, month: str) -> None:
        """
        Delete a PPI record by its month.
        
        Args:
            month (str): The month of the PPI record to delete
        """
        query = "DELETE FROM cn_ppi WHERE month = $1"
        await self.db.execute(query, month)
    
    async def list_ppi(self, limit: int = 20, offset: int = 0) -> List[CnPpiData]:
        """
        List PPI records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[CnPpiData]: List of PPI data
        """
        query = "SELECT * FROM cn_ppi ORDER BY month DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [CnPpiData(**row) for row in rows]
    
    async def get_ppi_range(self, start_month: str, end_month: str) -> List[CnPpiData]:
        """
        Retrieve PPI records within a month range.
        
        Args:
            start_month (str): The start month (inclusive)
            end_month (str): The end month (inclusive)
            
        Returns:
            list[CnPpiData]: List of PPI data within the month range
        """
        query = """
            SELECT * FROM cn_ppi 
            WHERE month >= $1 AND month <= $2
            ORDER BY month
        """
        rows = await self.db.fetch(query, start_month, end_month)
        return [CnPpiData(**row) for row in rows]
    
    async def get_latest_ppi(self) -> Optional[CnPpiData]:
        """
        Retrieve the most recent PPI record.
        
        Returns:
            CnPpiData | None: The most recent PPI data if found, None otherwise
        """
        query = "SELECT * FROM cn_ppi ORDER BY month DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return CnPpiData(**row) if row else None
    
    async def get_year_ppi(self, year: int) -> List[CnPpiData]:
        """
        Retrieve all PPI records for a specific year.
        
        Args:
            year (int): The year to retrieve data for
            
        Returns:
            list[CnPpiData]: List of PPI data for the specified year
        """
        start_month = f"{year}01"
        end_month = f"{year}12"
        
        query = """
            SELECT * FROM cn_ppi 
            WHERE month >= $1 AND month <= $2
            ORDER BY month
        """
        rows = await self.db.fetch(query, start_month, end_month)
        return [CnPpiData(**row) for row in rows]
    
    async def get_ppi_trend(self, months: int = 12) -> List[dict]:
        """
        Retrieve PPI trend for recent months.
        
        Args:
            months (int): Number of months to look back
            
        Returns:
            list[dict]: List of months and their PPI values
        """
        query = """
            SELECT month, ppi_yoy, ppi_mom, ppi_accu
            FROM cn_ppi 
            ORDER BY month DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, months)
        
        # Sort by month in ascending order for trend analysis
        result = [{"month": row["month"], "ppi_yoy": row["ppi_yoy"], "ppi_mom": row["ppi_mom"], "ppi_accu": row["ppi_accu"]} for row in rows]
        return sorted(result, key=lambda x: x["month"])
    
    async def get_ppi_mp_cp_comparison(self, months: int = 12) -> List[dict]:
        """
        Retrieve comparison data between production materials PPI and consumer goods PPI.
        
        Args:
            months (int): Number of months to look back
            
        Returns:
            list[dict]: List of comparison data
        """
        query = """
            SELECT month, ppi_mp_yoy, ppi_cg_yoy
            FROM cn_ppi 
            ORDER BY month DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, months)
        
        # Sort by month in ascending order for trend analysis
        result = [{"month": row["month"], "production_materials": row["ppi_mp_yoy"], "consumer_goods": row["ppi_cg_yoy"]} for row in rows]
        return sorted(result, key=lambda x: x["month"])

    async def get_all_ppi(self) -> List[CnPpiData]:
        """
        Retrieve all PPI records from the table.
        
        Returns:
            list[CnPpiData]: Complete list of PPI data
        """
        query = "SELECT * FROM cn_ppi ORDER BY month"
        rows = await self.db.fetch(query)
        return [CnPpiData(**row) for row in rows]