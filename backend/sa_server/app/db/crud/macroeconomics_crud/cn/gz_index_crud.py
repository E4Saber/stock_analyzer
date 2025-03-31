import datetime
from typing import List, Optional, Tuple
from app.data.db_modules.macroeconomics_modules.cn.gz_index import GzIndexData


class GzIndexCRUD:
    """
    CRUD operations for Guizhou Small Loan Market Interest Rate Index data.
    
    Provides methods to create, read, update, and delete index records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_index(self, data: GzIndexData) -> None:
        """
        Create a new Guizhou index record in the database.
        
        Args:
            data (GzIndexData): The index data to insert
        """
        query = """
            INSERT INTO gz_index (
                date, d10_rate, m1_rate, m3_rate, m6_rate, m12_rate, long_rate
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_index_by_date(self, date: datetime.date) -> Optional[GzIndexData]:
        """
        Retrieve a Guizhou index record by date.
        
        Args:
            date (datetime.date): The date of the index to retrieve
            
        Returns:
            GzIndexData | None: The index data if found, None otherwise
        """
        query = "SELECT * FROM gz_index WHERE date = $1"
        row = await self.db.fetchrow(query, date)
        return GzIndexData(**row) if row else None
    
    async def get_indices_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[GzIndexData]:
        """
        Retrieve Guizhou index records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[GzIndexData]: List of index data for the date range
        """
        query = """
            SELECT * FROM gz_index 
            WHERE date BETWEEN $1 AND $2
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [GzIndexData(**row) for row in rows]
    
    async def update_index(self, date: datetime.date, updates: dict) -> None:
        """
        Update a Guizhou index record by date.
        
        Args:
            date (datetime.date): The date of the index to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE gz_index
            SET {set_values}
            WHERE date = $1
        """
        await self.db.execute(query, date, *updates.values())
    
    async def delete_index(self, date: datetime.date) -> None:
        """
        Delete a Guizhou index record by date.
        
        Args:
            date (datetime.date): The date of the index to delete
        """
        query = "DELETE FROM gz_index WHERE date = $1"
        await self.db.execute(query, date)
    
    async def delete_indices_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Delete Guizhou index records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM gz_index WHERE date BETWEEN $1 AND $2"
        result = await self.db.execute(query, start_date, end_date)
        # 解析结果，格式类似 "DELETE 10"
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def list_indices(self, limit: int = 100, offset: int = 0) -> List[GzIndexData]:
        """
        List Guizhou index records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[GzIndexData]: List of index data
        """
        query = "SELECT * FROM gz_index ORDER BY date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [GzIndexData(**row) for row in rows]
    
    async def get_date_range(self) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Get the earliest and latest dates in the Guizhou index records.
        
        Returns:
            Tuple[datetime.date, datetime.date]: Tuple of (earliest_date, latest_date)
        """
        query = """
            SELECT 
                MIN(date) AS earliest_date,
                MAX(date) AS latest_date
            FROM gz_index
        """
        row = await self.db.fetchrow(query)
        return (row['earliest_date'], row['latest_date']) if row else (None, None)
    
    async def get_latest_index(self) -> Optional[GzIndexData]:
        """
        Get the latest Guizhou index record.
        
        Returns:
            GzIndexData | None: The latest index data if available, None otherwise
        """
        query = "SELECT * FROM gz_index ORDER BY date DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return GzIndexData(**row) if row else None
    
    async def get_count(self) -> int:
        """
        Get the total count of Guizhou index records.
        
        Returns:
            int: Count of records
        """
        query = "SELECT COUNT(*) FROM gz_index"
        result = await self.db.fetchval(query)
        return result
    
    async def get_monthly_average(self, year: int, month: int) -> Optional[dict]:
        """
        Calculate monthly average rates for a specific year and month.
        
        Args:
            year (int): Year
            month (int): Month (1-12)
            
        Returns:
            dict | None: Dictionary with average rates for each term or None if no data
        """
        # 构建月份的开始和结束日期
        start_date = datetime.date(year, month, 1)
        # 计算下个月的第一天，然后减去一天得到当月最后一天
        if month == 12:
            end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        
        query = """
            SELECT 
                AVG(d10_rate) AS avg_d10_rate,
                AVG(m1_rate) AS avg_m1_rate,
                AVG(m3_rate) AS avg_m3_rate,
                AVG(m6_rate) AS avg_m6_rate,
                AVG(m12_rate) AS avg_m12_rate,
                AVG(long_rate) AS avg_long_rate,
                COUNT(*) AS data_count
            FROM gz_index
            WHERE date BETWEEN $1 AND $2
        """
        
        row = await self.db.fetchrow(query, start_date, end_date)
        
        if row and row['data_count'] > 0:
            return {
                'year': year,
                'month': month,
                'd10_rate': row['avg_d10_rate'],
                'm1_rate': row['avg_m1_rate'],
                'm3_rate': row['avg_m3_rate'],
                'm6_rate': row['avg_m6_rate'],
                'm12_rate': row['avg_m12_rate'],
                'long_rate': row['avg_long_rate'],
                'days_count': row['data_count']
            }
        return None
    
    async def get_yearly_average(self, year: int) -> Optional[dict]:
        """
        Calculate yearly average rates for a specific year.
        
        Args:
            year (int): Year
            
        Returns:
            dict | None: Dictionary with average rates for each term or None if no data
        """
        # 构建年份的开始和结束日期
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        
        query = """
            SELECT 
                AVG(d10_rate) AS avg_d10_rate,
                AVG(m1_rate) AS avg_m1_rate,
                AVG(m3_rate) AS avg_m3_rate,
                AVG(m6_rate) AS avg_m6_rate,
                AVG(m12_rate) AS avg_m12_rate,
                AVG(long_rate) AS avg_long_rate,
                COUNT(*) AS data_count
            FROM gz_index
            WHERE date BETWEEN $1 AND $2
        """
        
        row = await self.db.fetchrow(query, start_date, end_date)
        
        if row and row['data_count'] > 0:
            return {
                'year': year,
                'd10_rate': row['avg_d10_rate'],
                'm1_rate': row['avg_m1_rate'],
                'm3_rate': row['avg_m3_rate'],
                'm6_rate': row['avg_m6_rate'],
                'm12_rate': row['avg_m12_rate'],
                'long_rate': row['avg_long_rate'],
                'days_count': row['data_count']
            }
        return None
    
    async def get_term_history(self, term: str, limit: int = 100) -> List[dict]:
        """
        Get historical data for a specific term.
        
        Args:
            term (str): Term to get history for ('d10', 'm1', 'm3', 'm6', 'm12', 'long')
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[dict]: List of date and rate pairs
        """
        # 验证期限参数
        valid_terms = {'d10', 'm1', 'm3', 'm6', 'm12', 'long'}
        if term not in valid_terms:
            raise ValueError(f"无效的期限参数，必须是以下之一: {valid_terms}")
        
        rate_column = f"{term}_rate"
        query = f"""
            SELECT date, {rate_column} as rate
            FROM gz_index
            WHERE {rate_column} IS NOT NULL
            ORDER BY date DESC
            LIMIT $1
        """
        
        rows = await self.db.fetch(query, limit)
        return [{'date': row['date'], 'rate': row['rate']} for row in rows]