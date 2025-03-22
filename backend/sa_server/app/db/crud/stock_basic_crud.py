from app.data.db_modules.stock_basic import StockBasicData


class StockBasicCRUD:
    """
    CRUD operations for stock data.
    
    Provides methods to create, read, update, and delete stock records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_stock(self, data: StockBasicData) -> None:
        """
        Create a new stock record in the database.
        
        Args:
            data (StockBasicData): The stock data to insert
        """
        query = """
            INSERT INTO stock_basic (
                ts_code, symbol, name, area, industry, fullname, enname,
                cnspell, market, exchange, curr_type, list_status,
                list_date, delist_date, is_hs, act_name, act_ent_type
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                $14, $15, $16, $17
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_stock_by_ts_code(self, ts_code: str) -> StockBasicData | None:
        """
        Retrieve a stock record by its TS code.
        
        Args:
            ts_code (str): The TS code of the stock to retrieve
            
        Returns:
            StockBasicData | None: The stock data if found, None otherwise
        """
        query = "SELECT * FROM stock_basic WHERE ts_code = $1"
        row = await self.db.fetchrow(query, ts_code)
        return StockBasicData(**row) if row else None
    
    async def get_stock_by_symbol(self, symbol: str) -> StockBasicData | None:
        """
        Retrieve a stock record by its symbol.
        
        Args:
            symbol (str): The symbol of the stock to retrieve
            
        Returns:
            StockBasicData | None: The stock data if found, None otherwise
        """
        query = "SELECT * FROM stock_basic WHERE symbol = $1"
        row = await self.db.fetchrow(query, symbol)
        return StockBasicData(**row) if row else None
    
    async def update_stock(self, ts_code: str, updates: dict) -> None:
        """
        Update a stock record by its TS code.
        
        Args:
            ts_code (str): The TS code of the stock to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE stock_basic
            SET {set_values}
            WHERE ts_code = $1
        """
        await self.db.execute(query, ts_code, *updates.values())
    
    async def delete_stock(self, ts_code: str) -> None:
        """
        Delete a stock record by its TS code.
        
        Args:
            ts_code (str): The TS code of the stock to delete
        """
        query = "DELETE FROM stock_basic WHERE ts_code = $1"
        await self.db.execute(query, ts_code)
    
    async def list_stocks(self, limit: int = 100, offset: int = 0) -> list[StockBasicData]:
        """
        List stocks with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[StockBasicData]: List of stock data
        """
        query = "SELECT * FROM stock_basic ORDER BY ts_code LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [StockBasicData(**row) for row in rows]
    
    async def search_stocks(self, search_term: str, limit: int = 100) -> list[StockBasicData]:
        """
        Search for stocks by name, symbol, or fullname.
        
        Args:
            search_term (str): Term to search for
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[StockBasicData]: List of stock data matching the search term
        """
        query = """
            SELECT * FROM stock_basic 
            WHERE name ILIKE $1 OR symbol ILIKE $1 OR fullname ILIKE $1
            ORDER BY ts_code 
            LIMIT $2
        """
        search_pattern = f"%{search_term}%"
        rows = await self.db.fetch(query, search_pattern, limit)
        return [StockBasicData(**row) for row in rows]