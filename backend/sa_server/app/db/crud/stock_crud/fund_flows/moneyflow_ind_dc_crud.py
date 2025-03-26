import datetime
from typing import List, Optional
from app.data.db_modules.stock_modules.fund_flows.moneyflow_ind_dc import MoneyflowIndDcData


class MoneyflowIndDcCRUD:
    """
    CRUD operations for DC industry/concept/region moneyflow data.
    
    Provides methods to create, read, update, and delete DC industry/concept/region moneyflow records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_moneyflow_ind_dc(self, data: MoneyflowIndDcData) -> None:
        """
        Create a new DC industry/concept/region moneyflow record in the database.
        
        Args:
            data (MoneyflowIndDcData): The DC industry/concept/region moneyflow data to insert
        """
        query = """
            INSERT INTO moneyflow_ind_dc (
                ts_code, trade_date, content_type, name, pct_change, close, net_amount, net_amount_rate,
                buy_elg_amount, buy_elg_amount_rate, buy_lg_amount, buy_lg_amount_rate,
                buy_md_amount, buy_md_amount_rate, buy_sm_amount, buy_sm_amount_rate,
                buy_sm_amount_stock, rank
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_moneyflow_ind_dc_by_key(self, ts_code: str, trade_date: datetime.date, content_type: str) -> Optional[MoneyflowIndDcData]:
        """
        Retrieve a DC industry/concept/region moneyflow record by its composite key.
        
        Args:
            ts_code (str): The sector code
            trade_date (datetime.date): The trading date
            content_type (str): The data type (industry, concept, region)
            
        Returns:
            MoneyflowIndDcData | None: The DC industry/concept/region moneyflow data if found, None otherwise
        """
        query = "SELECT * FROM moneyflow_ind_dc WHERE ts_code = $1 AND trade_date = $2 AND content_type = $3"
        row = await self.db.fetchrow(query, ts_code, trade_date, content_type)
        return MoneyflowIndDcData(**row) if row else None
    
    async def update_moneyflow_ind_dc(self, ts_code: str, trade_date: datetime.date, content_type: str, updates: dict) -> None:
        """
        Update a DC industry/concept/region moneyflow record by its composite key.
        
        Args:
            ts_code (str): The sector code
            trade_date (datetime.date): The trading date
            content_type (str): The data type (industry, concept, region)
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 4}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE moneyflow_ind_dc
            SET {set_values}
            WHERE ts_code = $1 AND trade_date = $2 AND content_type = $3
        """
        await self.db.execute(query, ts_code, trade_date, content_type, *updates.values())
    
    async def delete_moneyflow_ind_dc(self, ts_code: str, trade_date: datetime.date, content_type: str) -> None:
        """
        Delete a DC industry/concept/region moneyflow record by its composite key.
        
        Args:
            ts_code (str): The sector code
            trade_date (datetime.date): The trading date
            content_type (str): The data type (industry, concept, region)
        """
        query = "DELETE FROM moneyflow_ind_dc WHERE ts_code = $1 AND trade_date = $2 AND content_type = $3"
        await self.db.execute(query, ts_code, trade_date, content_type)
    
    async def get_moneyflow_ind_dc_by_ts_code(self, ts_code: str, content_type: Optional[str] = None, 
                                            limit: int = 100, offset: int = 0) -> List[MoneyflowIndDcData]:
        """
        Retrieve DC industry/concept/region moneyflow records by sector code with pagination.
        
        Args:
            ts_code (str): The sector code
            content_type (str, optional): The data type (industry, concept, region)
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowIndDcData]: List of DC industry/concept/region moneyflow data
        """
        if content_type:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE ts_code = $1 AND content_type = $2
                ORDER BY trade_date DESC 
                LIMIT $3 OFFSET $4
            """
            rows = await self.db.fetch(query, ts_code, content_type, limit, offset)
        else:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE ts_code = $1
                ORDER BY trade_date DESC 
                LIMIT $2 OFFSET $3
            """
            rows = await self.db.fetch(query, ts_code, limit, offset)
        return [MoneyflowIndDcData(**row) for row in rows]
    
    async def get_moneyflow_ind_dc_by_date_range(self, ts_code: str, start_date: datetime.date, 
                                               end_date: datetime.date, 
                                               content_type: Optional[str] = None) -> List[MoneyflowIndDcData]:
        """
        Retrieve DC industry/concept/region moneyflow records by sector code within a date range.
        
        Args:
            ts_code (str): The sector code
            start_date (datetime.date): Start date of the range (inclusive)
            end_date (datetime.date): End date of the range (inclusive)
            content_type (str, optional): The data type (industry, concept, region)
            
        Returns:
            list[MoneyflowIndDcData]: List of DC industry/concept/region moneyflow data
        """
        if content_type:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE ts_code = $1 
                AND trade_date BETWEEN $2 AND $3
                AND content_type = $4
                ORDER BY trade_date DESC
            """
            rows = await self.db.fetch(query, ts_code, start_date, end_date, content_type)
        else:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE ts_code = $1 
                AND trade_date BETWEEN $2 AND $3
                ORDER BY trade_date DESC
            """
            rows = await self.db.fetch(query, ts_code, start_date, end_date)
        return [MoneyflowIndDcData(**row) for row in rows]
    
    async def get_moneyflow_ind_dc_by_date(self, trade_date: datetime.date, content_type: Optional[str] = None,
                                         limit: int = 100, offset: int = 0) -> List[MoneyflowIndDcData]:
        """
        Retrieve DC industry/concept/region moneyflow records by trading date with pagination.
        
        Args:
            trade_date (datetime.date): The trading date
            content_type (str, optional): The data type (industry, concept, region)
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowIndDcData]: List of DC industry/concept/region moneyflow data
        """
        if content_type:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE trade_date = $1 AND content_type = $2
                ORDER BY net_amount DESC 
                LIMIT $3 OFFSET $4
            """
            rows = await self.db.fetch(query, trade_date, content_type, limit, offset)
        else:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE trade_date = $1
                ORDER BY net_amount DESC 
                LIMIT $2 OFFSET $3
            """
            rows = await self.db.fetch(query, trade_date, limit, offset)
        return [MoneyflowIndDcData(**row) for row in rows]
    
    async def get_top_inflow_sectors(self, trade_date: datetime.date, content_type: Optional[str] = None, 
                                   limit: int = 10) -> List[MoneyflowIndDcData]:
        """
        Retrieve sectors with the highest net inflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            content_type (str, optional): The data type (industry, concept, region)
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowIndDcData]: List of DC industry/concept/region moneyflow data
        """
        if content_type:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE trade_date = $1 AND content_type = $2
                ORDER BY net_amount DESC 
                LIMIT $3
            """
            rows = await self.db.fetch(query, trade_date, content_type, limit)
        else:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE trade_date = $1
                ORDER BY net_amount DESC 
                LIMIT $2
            """
            rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowIndDcData(**row) for row in rows]
    
    async def get_top_outflow_sectors(self, trade_date: datetime.date, content_type: Optional[str] = None, 
                                    limit: int = 10) -> List[MoneyflowIndDcData]:
        """
        Retrieve sectors with the highest net outflow on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            content_type (str, optional): The data type (industry, concept, region)
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowIndDcData]: List of DC industry/concept/region moneyflow data
        """
        if content_type:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE trade_date = $1 AND content_type = $2
                ORDER BY net_amount ASC 
                LIMIT $3
            """
            rows = await self.db.fetch(query, trade_date, content_type, limit)
        else:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE trade_date = $1
                ORDER BY net_amount ASC 
                LIMIT $2
            """
            rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowIndDcData(**row) for row in rows]
    
    async def get_rising_sectors(self, trade_date: datetime.date, content_type: Optional[str] = None, 
                               limit: int = 10) -> List[MoneyflowIndDcData]:
        """
        Retrieve sectors with the highest price increase on a specific date.
        
        Args:
            trade_date (datetime.date): The trading date
            content_type (str, optional): The data type (industry, concept, region)
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[MoneyflowIndDcData]: List of DC industry/concept/region moneyflow data
        """
        if content_type:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE trade_date = $1 AND content_type = $2
                ORDER BY pct_change DESC 
                LIMIT $3
            """
            rows = await self.db.fetch(query, trade_date, content_type, limit)
        else:
            query = """
                SELECT * FROM moneyflow_ind_dc 
                WHERE trade_date = $1
                ORDER BY pct_change DESC 
                LIMIT $2
            """
            rows = await self.db.fetch(query, trade_date, limit)
        return [MoneyflowIndDcData(**row) for row in rows]
    
    async def get_sectors_by_content_type(self, content_type: str, trade_date: datetime.date, 
                                        limit: int = 100, offset: int = 0) -> List[MoneyflowIndDcData]:
        """
        Retrieve sectors by content type on a specific date.
        
        Args:
            content_type (str): The data type (industry, concept, region)
            trade_date (datetime.date): The trading date
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[MoneyflowIndDcData]: List of DC industry/concept/region moneyflow data
        """
        query = """
            SELECT * FROM moneyflow_ind_dc 
            WHERE content_type = $1 AND trade_date = $2
            ORDER BY rank ASC 
            LIMIT $3 OFFSET $4
        """
        rows = await self.db.fetch(query, content_type, trade_date, limit, offset)
        return [MoneyflowIndDcData(**row) for row in rows]