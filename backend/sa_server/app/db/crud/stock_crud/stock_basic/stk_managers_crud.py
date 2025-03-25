from app.data.db_modules.stock_modules.stock_basic.stk_managers import StockManagerData


class StockManagerCRUD:
    """
    CRUD operations for stock managers data.
    
    Provides methods to create, read, update, and delete stock manager records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_manager(self, data: StockManagerData) -> int:
        """
        Create a new stock manager record in the database.
        
        Args:
            data (StockManagerData): The manager data to insert
            
        Returns:
            int: The ID of the newly created record
        """
        query = """
            INSERT INTO stk_managers (
                ts_code, ann_date, name, gender, lev, title, edu,
                national, birthday, begin_date, end_date, resume
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
            ) RETURNING id
        """
        # 移除id字段，因为它是自动生成的
        data_dict = data.model_dump(exclude={'id'})
        values = list(data_dict.values())
        
        return await self.db.fetchval(query, *values)

    async def get_manager_by_id(self, manager_id: int) -> StockManagerData | None:
        """
        Retrieve a manager record by its ID.
        
        Args:
            manager_id (int): The ID of the manager to retrieve
            
        Returns:
            StockManagerData | None: The manager data if found, None otherwise
        """
        query = "SELECT * FROM stk_managers WHERE id = $1"
        row = await self.db.fetchrow(query, manager_id)
        return StockManagerData(**row) if row else None
    
    async def get_managers_by_ts_code(self, ts_code: str) -> list[StockManagerData]:
        """
        Retrieve all manager records for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            list[StockManagerData]: List of manager data
        """
        query = "SELECT * FROM stk_managers WHERE ts_code = $1 ORDER BY begin_date DESC"
        rows = await self.db.fetch(query, ts_code)
        return [StockManagerData(**row) for row in rows]
    
    async def get_managers_by_name(self, name: str) -> list[StockManagerData]:
        """
        Retrieve all manager records by name.
        
        Args:
            name (str): The name of the manager
            
        Returns:
            list[StockManagerData]: List of manager data
        """
        query = "SELECT * FROM stk_managers WHERE name ILIKE $1 ORDER BY ts_code, begin_date DESC"
        search_pattern = f"%{name}%"
        rows = await self.db.fetch(query, search_pattern)
        return [StockManagerData(**row) for row in rows]
    
    async def get_current_managers(self, ts_code: str) -> list[StockManagerData]:
        """
        Retrieve current managers for a specific stock (where end_date is null).
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            list[StockManagerData]: List of current manager data
        """
        query = """
            SELECT * FROM stk_managers 
            WHERE ts_code = $1 AND end_date IS NULL 
            ORDER BY begin_date DESC
        """
        rows = await self.db.fetch(query, ts_code)
        return [StockManagerData(**row) for row in rows]
    
    async def update_manager(self, manager_id: int, updates: dict) -> None:
        """
        Update a manager record by its ID.
        
        Args:
            manager_id (int): The ID of the manager to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE stk_managers
            SET {set_values}
            WHERE id = $1
        """
        await self.db.execute(query, manager_id, *updates.values())
    
    async def delete_manager(self, manager_id: int) -> None:
        """
        Delete a manager record by its ID.
        
        Args:
            manager_id (int): The ID of the manager to delete
        """
        query = "DELETE FROM stk_managers WHERE id = $1"
        await self.db.execute(query, manager_id)
    
    async def delete_managers_by_ts_code(self, ts_code: str) -> int:
        """
        Delete all manager records for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM stk_managers WHERE ts_code = $1"
        result = await self.db.execute(query, ts_code)
        
        # 解析删除的记录数
        try:
            parts = result.split()
            return int(parts[1]) if len(parts) >= 2 else 0
        except (IndexError, ValueError):
            return 0
    
    async def list_managers(self, limit: int = 100, offset: int = 0) -> list[StockManagerData]:
        """
        List all managers with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[StockManagerData]: List of manager data
        """
        query = "SELECT * FROM stk_managers ORDER BY ts_code, name, begin_date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [StockManagerData(**row) for row in rows]
    
    async def search_managers(self, search_term: str, limit: int = 100) -> list[StockManagerData]:
        """
        Search for managers by name, title, or resume.
        
        Args:
            search_term (str): Term to search for
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[StockManagerData]: List of manager data matching the search term
        """
        query = """
            SELECT * FROM stk_managers 
            WHERE name ILIKE $1 OR title ILIKE $1 OR resume ILIKE $1
            ORDER BY ts_code, begin_date DESC 
            LIMIT $2
        """
        search_pattern = f"%{search_term}%"
        rows = await self.db.fetch(query, search_pattern, limit)
        return [StockManagerData(**row) for row in rows]