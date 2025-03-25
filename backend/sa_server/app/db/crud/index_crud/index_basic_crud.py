from app.data.db_modules.index_modules.index_basic import IndexBasicData


class IndexBasicCRUD:
    """
    CRUD operations for index data.
    
    Provides methods to create, read, update, and delete index records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_index(self, data: IndexBasicData) -> None:
        """
        Create a new index record in the database.
        
        Args:
            data (IndexBasicData): The index data to insert
        """
        query = """
            INSERT INTO index_basic (
                ts_code, name, fullname, market, publisher, index_type,
                category, base_date, base_point, list_date, weight_rule,
                description, exp_date
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_index_by_ts_code(self, ts_code: str) -> IndexBasicData | None:
        """
        Retrieve an index record by its TS code.
        
        Args:
            ts_code (str): The TS code of the index to retrieve
            
        Returns:
            IndexBasicData | None: The index data if found, None otherwise
        """
        query = "SELECT * FROM index_basic WHERE ts_code = $1"
        row = await self.db.fetchrow(query, ts_code)
        return IndexBasicData(**row) if row else None
    
    async def get_index_by_name(self, name: str) -> IndexBasicData | None:
        """
        Retrieve an index record by its name.
        
        Args:
            name (str): The name of the index to retrieve
            
        Returns:
            IndexBasicData | None: The index data if found, None otherwise
        """
        query = "SELECT * FROM index_basic WHERE name = $1"
        row = await self.db.fetchrow(query, name)
        return IndexBasicData(**row) if row else None
    
    async def update_index(self, ts_code: str, updates: dict) -> None:
        """
        Update an index record by its TS code.
        
        Args:
            ts_code (str): The TS code of the index to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE index_basic
            SET {set_values}
            WHERE ts_code = $1
        """
        await self.db.execute(query, ts_code, *updates.values())
    
    async def delete_index(self, ts_code: str) -> None:
        """
        Delete an index record by its TS code.
        
        Args:
            ts_code (str): The TS code of the index to delete
        """
        query = "DELETE FROM index_basic WHERE ts_code = $1"
        await self.db.execute(query, ts_code)
    
    async def list_indexes(self, limit: int = 100, offset: int = 0) -> list[IndexBasicData]:
        """
        List indexes with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[IndexBasicData]: List of index data
        """
        query = "SELECT * FROM index_basic ORDER BY ts_code LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [IndexBasicData(**row) for row in rows]
    
    async def search_indexes(self, search_term: str, limit: int = 100) -> list[IndexBasicData]:
        """
        Search for indexes by name or fullname.
        
        Args:
            search_term (str): Term to search for
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[IndexBasicData]: List of index data matching the search term
        """
        query = """
            SELECT * FROM index_basic 
            WHERE name ILIKE $1 OR fullname ILIKE $1
            ORDER BY ts_code 
            LIMIT $2
        """
        search_pattern = f"%{search_term}%"
        rows = await self.db.fetch(query, search_pattern, limit)
        return [IndexBasicData(**row) for row in rows]
        
    async def filter_indexes_by_market(self, market: str, limit: int = 100, offset: int = 0) -> list[IndexBasicData]:
        """
        Filter indexes by market.
        
        Args:
            market (str): Market to filter by
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[IndexBasicData]: List of index data matching the market
        """
        query = """
            SELECT * FROM index_basic 
            WHERE market = $1
            ORDER BY ts_code 
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, market, limit, offset)
        return [IndexBasicData(**row) for row in rows]
        
    async def filter_indexes_by_category(self, category: str, limit: int = 100, offset: int = 0) -> list[IndexBasicData]:
        """
        Filter indexes by category.
        
        Args:
            category (str): Category to filter by
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[IndexBasicData]: List of index data matching the category
        """
        query = """
            SELECT * FROM index_basic 
            WHERE category = $1
            ORDER BY ts_code 
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, category, limit, offset)
        return [IndexBasicData(**row) for row in rows]