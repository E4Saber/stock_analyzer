import datetime
from typing import List, Optional, Tuple
from app.data.db_modules.macroeconomics_modules.cn.shibor_quote import ShiborQuoteData


class ShiborQuoteCRUD:
    """
    CRUD operations for SHIBOR quote data.
    
    Provides methods to create, read, update, and delete SHIBOR quote records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_quote(self, data: ShiborQuoteData) -> None:
        """
        Create a new SHIBOR quote record in the database.
        
        Args:
            data (ShiborQuoteData): The SHIBOR quote data to insert
        """
        query = """
            INSERT INTO shibor_quote (
                date, bank, on_b, on_a, w1_b, w1_a, w2_b, w2_a,
                m1_b, m1_a, m3_b, m3_a, m6_b, m6_a, m9_b, m9_a, y1_b, y1_a
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                $14, $15, $16, $17, $18
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_quote_by_date_bank(self, date: datetime.date, bank: str) -> Optional[ShiborQuoteData]:
        """
        Retrieve a SHIBOR quote record by date and bank.
        
        Args:
            date (datetime.date): The date of the quote
            bank (str): The bank name
            
        Returns:
            ShiborQuoteData | None: The SHIBOR quote data if found, None otherwise
        """
        query = "SELECT * FROM shibor_quote WHERE date = $1 AND bank = $2"
        row = await self.db.fetchrow(query, date, bank)
        return ShiborQuoteData(**row) if row else None
    
    async def get_quotes_by_date(self, date: datetime.date) -> List[ShiborQuoteData]:
        """
        Retrieve all SHIBOR quote records for a specific date.
        
        Args:
            date (datetime.date): The date to retrieve quotes for
            
        Returns:
            List[ShiborQuoteData]: List of SHIBOR quote data for the date
        """
        query = "SELECT * FROM shibor_quote WHERE date = $1 ORDER BY bank"
        rows = await self.db.fetch(query, date)
        return [ShiborQuoteData(**row) for row in rows]
    
    async def get_quotes_by_bank(self, bank: str, limit: int = 100, offset: int = 0) -> List[ShiborQuoteData]:
        """
        Retrieve SHIBOR quote records for a specific bank with pagination.
        
        Args:
            bank (str): The bank name
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[ShiborQuoteData]: List of SHIBOR quote data for the bank
        """
        query = "SELECT * FROM shibor_quote WHERE bank = $1 ORDER BY date DESC LIMIT $2 OFFSET $3"
        rows = await self.db.fetch(query, bank, limit, offset)
        return [ShiborQuoteData(**row) for row in rows]
    
    async def get_quotes_by_date_range(self, start_date: datetime.date, end_date: datetime.date, 
                                      bank: Optional[str] = None) -> List[ShiborQuoteData]:
        """
        Retrieve SHIBOR quote records for a date range and optionally for a specific bank.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            bank (str, optional): Bank name to filter by
            
        Returns:
            List[ShiborQuoteData]: List of SHIBOR quote data for the date range
        """
        if bank:
            query = """
                SELECT * FROM shibor_quote 
                WHERE date BETWEEN $1 AND $2 AND bank = $3
                ORDER BY date DESC, bank
            """
            rows = await self.db.fetch(query, start_date, end_date, bank)
        else:
            query = """
                SELECT * FROM shibor_quote 
                WHERE date BETWEEN $1 AND $2
                ORDER BY date DESC, bank
            """
            rows = await self.db.fetch(query, start_date, end_date)
        
        return [ShiborQuoteData(**row) for row in rows]
    
    async def update_quote(self, date: datetime.date, bank: str, updates: dict) -> None:
        """
        Update a SHIBOR quote record by date and bank.
        
        Args:
            date (datetime.date): The date of the quote to update
            bank (str): The bank name of the quote to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 3}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE shibor_quote
            SET {set_values}
            WHERE date = $1 AND bank = $2
        """
        await self.db.execute(query, date, bank, *updates.values())
    
    async def delete_quote(self, date: datetime.date, bank: str) -> None:
        """
        Delete a SHIBOR quote record by date and bank.
        
        Args:
            date (datetime.date): The date of the quote to delete
            bank (str): The bank name of the quote to delete
        """
        query = "DELETE FROM shibor_quote WHERE date = $1 AND bank = $2"
        await self.db.execute(query, date, bank)
    
    async def delete_quotes_by_date(self, date: datetime.date) -> int:
        """
        Delete all SHIBOR quote records for a specific date.
        
        Args:
            date (datetime.date): The date to delete quotes for
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM shibor_quote WHERE date = $1"
        result = await self.db.execute(query, date)
        # 解析结果，格式类似 "DELETE 10"
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def list_quotes(self, limit: int = 100, offset: int = 0) -> List[ShiborQuoteData]:
        """
        List SHIBOR quotes with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[ShiborQuoteData]: List of SHIBOR quote data
        """
        query = "SELECT * FROM shibor_quote ORDER BY date DESC, bank LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [ShiborQuoteData(**row) for row in rows]
    
    async def get_date_range(self) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Get the earliest and latest dates in the SHIBOR quote records.
        
        Returns:
            Tuple[datetime.date, datetime.date]: Tuple of (earliest_date, latest_date)
        """
        query = """
            SELECT 
                MIN(date) AS earliest_date,
                MAX(date) AS latest_date
            FROM shibor_quote
        """
        row = await self.db.fetchrow(query)
        return (row['earliest_date'], row['latest_date']) if row else (None, None)
    
    async def get_bank_list(self) -> List[str]:
        """
        Get a list of all banks in the SHIBOR quote records.
        
        Returns:
            List[str]: List of bank names
        """
        query = "SELECT DISTINCT bank FROM shibor_quote ORDER BY bank"
        rows = await self.db.fetch(query)
        return [row['bank'] for row in rows]