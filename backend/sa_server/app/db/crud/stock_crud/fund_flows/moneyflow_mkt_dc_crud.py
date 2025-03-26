import datetime
from typing import List, Optional
from app.data.db_modules.stock_modules.fund_flows.moneyflow_mkt_dc import MoneyflowMktDcData


class MoneyflowMktDcCRUD:
    """
    CRUD operations for DC market moneyflow data.
    
    Provides methods to create, read, update, and delete DC market moneyflow records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_moneyflow_mkt_dc(self, data: MoneyflowMktDcData) -> None:
        """
        Create a new DC market moneyflow record in the database.
        
        Args:
            data (MoneyflowMktDcData): The DC market moneyflow data to insert
        """
        query = """
            INSERT INTO moneyflow_mkt_dc (
                trade_date, close_sh, pct_change_sh, close_sz, pct_change_sz, 
                net_amount, net_amount_rate, buy_elg_amount, buy_elg_amount_rate,
                buy_lg_amount, buy_lg_amount_rate, buy_md_amount, buy_md_amount_rate,
                buy_sm_amount, buy_sm_amount_rate
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_moneyflow_mkt_dc_by_date(self, trade_date: datetime.date) -> Optional[MoneyflowMktDcData]:
        """
        Retrieve a DC market moneyflow record by its date.
        
        Args:
            trade_date (datetime.date): The trading date
            
        Returns:
            MoneyflowMktDcData | None: The DC market moneyflow data if found, None otherwise
        """
        query = "SELECT * FROM moneyflow_mkt_dc WHERE trade_date = $1"
        row = await self.db.fetchrow(query, trade_date)
        return MoneyflowMktDcData(**row) if row else None
    
    async def update_moneyflow_mkt_dc(self, trade_date: datetime.date, updates: dict) -> None:
        """
        Update a DC market moneyflow record by its date.
        
        Args:
            trade_date (datetime.date): The trading date
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE moneyflow_mkt_dc
            SET {set_values}
            WHERE trade_date = $1
        """
        await self.db.execute(query, trade_date, *updates.values())
    
    async def delete_moneyflow_mkt_dc(self, trade_date: datetime.date) -> None:
        """
        Delete a DC market moneyflow record by its date.
        
        Args:
            trade_date (datetime.date): The trading date
        """
        query = "DELETE FROM moneyflow_mkt_dc WHERE trade_date = $1"
        await self.db.execute(query, trade_date)
    
    async def get_moneyflow_mkt_dc_by_date_range(self, start_date: datetime.date, 
                                               end_date: datetime.date) -> List[MoneyflowMktDcData]:
        """
        Retrieve DC market moneyflow records within a date range.
        
        Args:
            start_date (datetime.date): Start date of the range (inclusive)
            end_date (datetime.date): End date of the range (inclusive)
            
        Returns:
            list[MoneyflowMktDcData]: List of DC market moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_mkt_dc 
            WHERE trade_date BETWEEN $1 AND $2
            ORDER BY trade_date DESC
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [MoneyflowMktDcData(**row) for row in rows]
    
    async def list_moneyflow_mkt_dc(self, limit: int = 100, offset: int = 0) -> List[MoneyflowMktDcData]:
        """
        List DC market moneyflow records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowMktDcData]: List of DC market moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_mkt_dc 
            ORDER BY trade_date DESC 
            LIMIT $1 OFFSET $2
        """
        rows = await self.db.fetch(query, limit, offset)
        return [MoneyflowMktDcData(**row) for row in rows]
    
    async def get_positive_sh_days(self, limit: int = 100, offset: int = 0) -> List[MoneyflowMktDcData]:
        """
        Retrieve days with positive Shanghai market change.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowMktDcData]: List of DC market moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_mkt_dc 
            WHERE pct_change_sh > 0
            ORDER BY trade_date DESC 
            LIMIT $1 OFFSET $2
        """
        rows = await self.db.fetch(query, limit, offset)
        return [MoneyflowMktDcData(**row) for row in rows]
    
    async def get_negative_sh_days(self, limit: int = 100, offset: int = 0) -> List[MoneyflowMktDcData]:
        """
        Retrieve days with negative Shanghai market change.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowMktDcData]: List of DC market moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_mkt_dc 
            WHERE pct_change_sh < 0
            ORDER BY trade_date DESC 
            LIMIT $1 OFFSET $2
        """
        rows = await self.db.fetch(query, limit, offset)
        return [MoneyflowMktDcData(**row) for row in rows]
    
    async def get_top_inflow_days(self, limit: int = 10) -> List[MoneyflowMktDcData]:
        """
        Retrieve days with the highest net inflow.
        
        Args:
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowMktDcData]: List of DC market moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_mkt_dc 
            ORDER BY net_amount DESC 
            LIMIT $1
        """
        rows = await self.db.fetch(query, limit)
        return [MoneyflowMktDcData(**row) for row in rows]
    
    async def get_top_outflow_days(self, limit: int = 10) -> List[MoneyflowMktDcData]:
        """
        Retrieve days with the highest net outflow.
        
        Args:
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowMktDcData]: List of DC market moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_mkt_dc 
            ORDER BY net_amount ASC 
            LIMIT $1
        """
        rows = await self.db.fetch(query, limit)
        return [MoneyflowMktDcData(**row) for row in rows]
    
    async def get_latest_moneyflow_mkt_dc(self) -> Optional[MoneyflowMktDcData]:
        """
        Retrieve the most recent DC market moneyflow record.
        
        Returns:
            MoneyflowMktDcData | None: The latest DC market moneyflow data if found, None otherwise
        """
        query = """
            SELECT * FROM moneyflow_mkt_dc 
            ORDER BY trade_date DESC 
            LIMIT 1
        """
        row = await self.db.fetchrow(query)
        return MoneyflowMktDcData(**row) if row else None
    
    async def get_market_trend(self, days: int = 5) -> List[MoneyflowMktDcData]:
        """
        Retrieve the most recent days to analyze market trend.
        
        Args:
            days (int): Number of most recent days to retrieve
            
        Returns:
            list[MoneyflowMktDcData]: List of DC market moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_mkt_dc 
            ORDER BY trade_date DESC 
            LIMIT $1
        """
        rows = await self.db.fetch(query, days)
        return [MoneyflowMktDcData(**row) for row in rows]