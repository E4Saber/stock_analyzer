import datetime
from typing import List, Optional
from app.data.db_modules.stock_modules.fund_flows.moneyflow_hsgt import MoneyflowHsgtData


class MoneyflowHsgtCRUD:
    """
    CRUD operations for Hong Kong-Mainland stock connect moneyflow data.
    
    Provides methods to create, read, update, and delete HSGT moneyflow records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_moneyflow_hsgt(self, data: MoneyflowHsgtData) -> None:
        """
        Create a new HSGT moneyflow record in the database.
        
        Args:
            data (MoneyflowHsgtData): The HSGT moneyflow data to insert
        """
        query = """
            INSERT INTO moneyflow_hsgt (
                trade_date, ggt_ss, ggt_sz, hgt, sgt, north_money, south_money
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_moneyflow_hsgt_by_date(self, trade_date: datetime.date) -> Optional[MoneyflowHsgtData]:
        """
        Retrieve a HSGT moneyflow record by its date.
        
        Args:
            trade_date (datetime.date): The trading date
            
        Returns:
            MoneyflowHsgtData | None: The HSGT moneyflow data if found, None otherwise
        """
        query = "SELECT * FROM moneyflow_hsgt WHERE trade_date = $1"
        row = await self.db.fetchrow(query, trade_date)
        return MoneyflowHsgtData(**row) if row else None
    
    async def update_moneyflow_hsgt(self, trade_date: datetime.date, updates: dict) -> None:
        """
        Update a HSGT moneyflow record by its date.
        
        Args:
            trade_date (datetime.date): The trading date
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE moneyflow_hsgt
            SET {set_values}
            WHERE trade_date = $1
        """
        await self.db.execute(query, trade_date, *updates.values())
    
    async def delete_moneyflow_hsgt(self, trade_date: datetime.date) -> None:
        """
        Delete a HSGT moneyflow record by its date.
        
        Args:
            trade_date (datetime.date): The trading date
        """
        query = "DELETE FROM moneyflow_hsgt WHERE trade_date = $1"
        await self.db.execute(query, trade_date)
    
    async def get_moneyflow_hsgt_by_date_range(self, start_date: datetime.date, 
                                             end_date: datetime.date) -> List[MoneyflowHsgtData]:
        """
        Retrieve HSGT moneyflow records within a date range.
        
        Args:
            start_date (datetime.date): Start date of the range (inclusive)
            end_date (datetime.date): End date of the range (inclusive)
            
        Returns:
            list[MoneyflowHsgtData]: List of HSGT moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_hsgt 
            WHERE trade_date BETWEEN $1 AND $2
            ORDER BY trade_date DESC
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [MoneyflowHsgtData(**row) for row in rows]
    
    async def list_moneyflow_hsgt(self, limit: int = 100, offset: int = 0) -> List[MoneyflowHsgtData]:
        """
        List HSGT moneyflow records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowHsgtData]: List of HSGT moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_hsgt 
            ORDER BY trade_date DESC 
            LIMIT $1 OFFSET $2
        """
        rows = await self.db.fetch(query, limit, offset)
        return [MoneyflowHsgtData(**row) for row in rows]
    
    async def get_top_north_inflow_days(self, limit: int = 10) -> List[MoneyflowHsgtData]:
        """
        Retrieve days with the highest northbound inflow.
        
        Args:
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowHsgtData]: List of HSGT moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_hsgt 
            ORDER BY north_money DESC 
            LIMIT $1
        """
        rows = await self.db.fetch(query, limit)
        return [MoneyflowHsgtData(**row) for row in rows]
    
    async def get_top_north_outflow_days(self, limit: int = 10) -> List[MoneyflowHsgtData]:
        """
        Retrieve days with the highest northbound outflow.
        
        Args:
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowHsgtData]: List of HSGT moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_hsgt 
            ORDER BY north_money ASC 
            LIMIT $1
        """
        rows = await self.db.fetch(query, limit)
        return [MoneyflowHsgtData(**row) for row in rows]
    
    async def get_top_south_inflow_days(self, limit: int = 10) -> List[MoneyflowHsgtData]:
        """
        Retrieve days with the highest southbound inflow.
        
        Args:
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowHsgtData]: List of HSGT moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_hsgt 
            ORDER BY south_money DESC 
            LIMIT $1
        """
        rows = await self.db.fetch(query, limit)
        return [MoneyflowHsgtData(**row) for row in rows]
    
    async def get_top_south_outflow_days(self, limit: int = 10) -> List[MoneyflowHsgtData]:
        """
        Retrieve days with the highest southbound outflow.
        
        Args:
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowHsgtData]: List of HSGT moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_hsgt 
            ORDER BY south_money ASC 
            LIMIT $1
        """
        rows = await self.db.fetch(query, limit)
        return [MoneyflowHsgtData(**row) for row in rows]
    
    async def get_latest_moneyflow_hsgt(self) -> Optional[MoneyflowHsgtData]:
        """
        Retrieve the most recent HSGT moneyflow record.
        
        Returns:
            MoneyflowHsgtData | None: The latest HSGT moneyflow data if found, None otherwise
        """
        query = """
            SELECT * FROM moneyflow_hsgt 
            ORDER BY trade_date DESC 
            LIMIT 1
        """
        row = await self.db.fetchrow(query)
        return MoneyflowHsgtData(**row) if row else None