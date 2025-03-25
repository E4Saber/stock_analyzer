from app.data.db_modules.stock_modules.stock_basic.stk_rewards import StockRewardData


class StockRewardCRUD:
    """
    CRUD operations for stock manager rewards data.
    
    Provides methods to create, read, update, and delete stock manager reward records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_reward(self, data: StockRewardData) -> int:
        """
        Create a new stock manager reward record in the database.
        
        Args:
            data (StockRewardData): The reward data to insert
            
        Returns:
            int: The ID of the newly created record
        """
        query = """
            INSERT INTO stk_rewards (
                ts_code, ann_date, end_date, name, title, reward, hold_vol
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7
            ) RETURNING id
        """
        # 移除id字段，因为它是自动生成的
        data_dict = data.model_dump(exclude={'id'})
        values = list(data_dict.values())
        
        return await self.db.fetchval(query, *values)

    async def get_reward_by_id(self, reward_id: int) -> StockRewardData | None:
        """
        Retrieve a reward record by its ID.
        
        Args:
            reward_id (int): The ID of the reward record to retrieve
            
        Returns:
            StockRewardData | None: The reward data if found, None otherwise
        """
        query = "SELECT * FROM stk_rewards WHERE id = $1"
        row = await self.db.fetchrow(query, reward_id)
        return StockRewardData(**row) if row else None
    
    async def get_rewards_by_ts_code(self, ts_code: str) -> list[StockRewardData]:
        """
        Retrieve all reward records for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            list[StockRewardData]: List of reward data
        """
        query = "SELECT * FROM stk_rewards WHERE ts_code = $1 ORDER BY end_date DESC"
        rows = await self.db.fetch(query, ts_code)
        return [StockRewardData(**row) for row in rows]
    
    async def get_rewards_by_name(self, name: str) -> list[StockRewardData]:
        """
        Retrieve all reward records by manager name.
        
        Args:
            name (str): The name of the manager
            
        Returns:
            list[StockRewardData]: List of reward data
        """
        query = "SELECT * FROM stk_rewards WHERE name ILIKE $1 ORDER BY ts_code, end_date DESC"
        search_pattern = f"%{name}%"
        rows = await self.db.fetch(query, search_pattern)
        return [StockRewardData(**row) for row in rows]
    
    async def get_rewards_by_year(self, ts_code: str, year: int) -> list[StockRewardData]:
        """
        Retrieve reward records for a specific stock in a specific year.
        
        Args:
            ts_code (str): The TS code of the stock
            year (int): The year to filter by
            
        Returns:
            list[StockRewardData]: List of reward data
        """
        query = """
            SELECT * FROM stk_rewards 
            WHERE ts_code = $1 AND EXTRACT(YEAR FROM end_date) = $2
            ORDER BY end_date DESC
        """
        rows = await self.db.fetch(query, ts_code, year)
        return [StockRewardData(**row) for row in rows]
    
    async def update_reward(self, reward_id: int, updates: dict) -> None:
        """
        Update a reward record by its ID.
        
        Args:
            reward_id (int): The ID of the reward record to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE stk_rewards
            SET {set_values}
            WHERE id = $1
        """
        await self.db.execute(query, reward_id, *updates.values())
    
    async def delete_reward(self, reward_id: int) -> None:
        """
        Delete a reward record by its ID.
        
        Args:
            reward_id (int): The ID of the reward record to delete
        """
        query = "DELETE FROM stk_rewards WHERE id = $1"
        await self.db.execute(query, reward_id)
    
    async def delete_rewards_by_ts_code(self, ts_code: str) -> int:
        """
        Delete all reward records for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM stk_rewards WHERE ts_code = $1"
        result = await self.db.execute(query, ts_code)
        
        # 解析删除的记录数
        try:
            parts = result.split()
            return int(parts[1]) if len(parts) >= 2 else 0
        except (IndexError, ValueError):
            return 0
    
    async def list_rewards(self, limit: int = 100, offset: int = 0) -> list[StockRewardData]:
        """
        List all reward records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[StockRewardData]: List of reward data
        """
        query = "SELECT * FROM stk_rewards ORDER BY ts_code, end_date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [StockRewardData(**row) for row in rows]
    
    async def get_top_rewards(self, year: int, limit: int = 20) -> list[StockRewardData]:
        """
        Get top rewarded managers in a specific year.
        
        Args:
            year (int): The year to filter by
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[StockRewardData]: List of top reward data
        """
        query = """
            SELECT * FROM stk_rewards 
            WHERE EXTRACT(YEAR FROM end_date) = $1
            ORDER BY reward DESC NULLS LAST 
            LIMIT $2
        """
        rows = await self.db.fetch(query, year, limit)
        return [StockRewardData(**row) for row in rows]
    
    async def get_top_shareholders(self, year: int, limit: int = 20) -> list[StockRewardData]:
        """
        Get top shareholding managers in a specific year.
        
        Args:
            year (int): The year to filter by
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[StockRewardData]: List of top shareholding data
        """
        query = """
            SELECT * FROM stk_rewards 
            WHERE EXTRACT(YEAR FROM end_date) = $1
            ORDER BY hold_vol DESC NULLS LAST 
            LIMIT $2
        """
        rows = await self.db.fetch(query, year, limit)
        return [StockRewardData(**row) for row in rows]