from app.data.db_modules.stock_modules.stock_basic.new_share import NewShareData


class NewShareCRUD:
    """
    CRUD operations for IPO new shares data.
    
    Provides methods to create, read, update, and delete new share records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_new_share(self, data: NewShareData) -> str:
        """
        Create a new IPO share record in the database.
        
        Args:
            data (NewShareData): The new share data to insert
            
        Returns:
            str: The ts_code of the newly created record
        """
        query = """
            INSERT INTO new_share (
                ts_code, sub_code, name, ipo_date, issue_date, amount,
                market_amount, price, pe, limit_amount, funds, ballot
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
            ) RETURNING ts_code
        """
        data_dict = data.model_dump()
        values = list(data_dict.values())
        
        return await self.db.fetchval(query, *values)

    async def get_new_share_by_ts_code(self, ts_code: str) -> NewShareData | None:
        """
        Retrieve a new share record by its TS code.
        
        Args:
            ts_code (str): The TS code of the new share to retrieve
            
        Returns:
            NewShareData | None: The new share data if found, None otherwise
        """
        query = "SELECT * FROM new_share WHERE ts_code = $1"
        row = await self.db.fetchrow(query, ts_code)
        return NewShareData(**row) if row else None
    
    async def get_new_share_by_sub_code(self, sub_code: str) -> NewShareData | None:
        """
        Retrieve a new share record by its subscription code.
        
        Args:
            sub_code (str): The subscription code of the new share to retrieve
            
        Returns:
            NewShareData | None: The new share data if found, None otherwise
        """
        query = "SELECT * FROM new_share WHERE sub_code = $1"
        row = await self.db.fetchrow(query, sub_code)
        return NewShareData(**row) if row else None
    
    async def update_new_share(self, ts_code: str, updates: dict) -> None:
        """
        Update a new share record by its TS code.
        
        Args:
            ts_code (str): The TS code of the new share to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE new_share
            SET {set_values}
            WHERE ts_code = $1
        """
        await self.db.execute(query, ts_code, *updates.values())
    
    async def delete_new_share(self, ts_code: str) -> None:
        """
        Delete a new share record by its TS code.
        
        Args:
            ts_code (str): The TS code of the new share to delete
        """
        query = "DELETE FROM new_share WHERE ts_code = $1"
        await self.db.execute(query, ts_code)
    
    async def list_new_shares(self, limit: int = 100, offset: int = 0) -> list[NewShareData]:
        """
        List new shares with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[NewShareData]: List of new share data
        """
        query = "SELECT * FROM new_share ORDER BY ipo_date DESC NULLS LAST, ts_code LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [NewShareData(**row) for row in rows]
    
    async def get_new_shares_by_period(self, start_date: str, end_date: str) -> list[NewShareData]:
        """
        Retrieve new shares within a specific period by IPO date.
        
        Args:
            start_date (str): Start date of the period (format: YYYY-MM-DD)
            end_date (str): End date of the period (format: YYYY-MM-DD)
            
        Returns:
            list[NewShareData]: List of new share data in the period
        """
        query = """
            SELECT * FROM new_share 
            WHERE ipo_date BETWEEN $1 AND $2
            ORDER BY ipo_date, ts_code
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [NewShareData(**row) for row in rows]
    
    async def get_listed_by_period(self, start_date: str, end_date: str) -> list[NewShareData]:
        """
        Retrieve new shares that were listed within a specific period.
        
        Args:
            start_date (str): Start date of the period (format: YYYY-MM-DD)
            end_date (str): End date of the period (format: YYYY-MM-DD)
            
        Returns:
            list[NewShareData]: List of new share data in the period
        """
        query = """
            SELECT * FROM new_share 
            WHERE issue_date BETWEEN $1 AND $2
            ORDER BY issue_date, ts_code
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [NewShareData(**row) for row in rows]
    
    async def get_high_pe_shares(self, pe_threshold: float = 50.0) -> list[NewShareData]:
        """
        Retrieve new shares with high PE ratio.
        
        Args:
            pe_threshold (float): PE ratio threshold
            
        Returns:
            list[NewShareData]: List of new share data with high PE ratio
        """
        query = """
            SELECT * FROM new_share 
            WHERE pe > $1
            ORDER BY pe DESC, ipo_date DESC
        """
        rows = await self.db.fetch(query, pe_threshold)
        return [NewShareData(**row) for row in rows]
    
    async def get_large_fundraising(self, funds_threshold: float = 50.0) -> list[NewShareData]:
        """
        Retrieve new shares with large fundraising amount.
        
        Args:
            funds_threshold (float): Fundraising amount threshold (100 million CNY)
            
        Returns:
            list[NewShareData]: List of new share data with large fundraising
        """
        query = """
            SELECT * FROM new_share 
            WHERE funds > $1
            ORDER BY funds DESC, ipo_date DESC
        """
        rows = await self.db.fetch(query, funds_threshold)
        return [NewShareData(**row) for row in rows]