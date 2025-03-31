import datetime
from typing import List, Optional, Tuple, Dict, Any
from app.data.db_modules.macroeconomics_modules.us.us_trltr import UsTrltrData


class UsTrltrCRUD:
    """
    CRUD operations for US Treasury Real Long-term Rates data.
    
    Provides methods to create, read, update, and delete real long-term treasury rates records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_trltr(self, data: UsTrltrData) -> None:
        """
        Create a new US Treasury Real Long-term Rates record in the database.
        
        Args:
            data (UsTrltrData): The real long-term treasury rates data to insert
        """
        query = """
            INSERT INTO us_trltr (
                date, ltr_avg
            ) VALUES (
                $1, $2
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_trltr_by_date(self, date: datetime.date) -> Optional[UsTrltrData]:
        """
        Retrieve a US Treasury Real Long-term Rates record by date.
        
        Args:
            date (datetime.date): The date of the real long-term treasury rates to retrieve
            
        Returns:
            UsTrltrData | None: The real long-term treasury rates data if found, None otherwise
        """
        query = "SELECT * FROM us_trltr WHERE date = $1"
        row = await self.db.fetchrow(query, date)
        return UsTrltrData(**row) if row else None
    
    async def get_trltr_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[UsTrltrData]:
        """
        Retrieve US Treasury Real Long-term Rates records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[UsTrltrData]: List of real long-term treasury rates data for the date range
        """
        query = """
            SELECT * FROM us_trltr 
            WHERE date BETWEEN $1 AND $2
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [UsTrltrData(**row) for row in rows]
    
    async def update_trltr(self, date: datetime.date, ltr_avg: float) -> None:
        """
        Update a US Treasury Real Long-term Rates record by date.
        
        Args:
            date (datetime.date): The date of the real long-term treasury rates to update
            ltr_avg (float): The new LT Real Average rate value
        """
        query = "UPDATE us_trltr SET ltr_avg = $2 WHERE date = $1"
        await self.db.execute(query, date, ltr_avg)
    
    async def delete_trltr(self, date: datetime.date) -> None:
        """
        Delete a US Treasury Real Long-term Rates record by date.
        
        Args:
            date (datetime.date): The date of the real long-term treasury rates to delete
        """
        query = "DELETE FROM us_trltr WHERE date = $1"
        await self.db.execute(query, date)
    
    async def delete_trltr_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Delete US Treasury Real Long-term Rates records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM us_trltr WHERE date BETWEEN $1 AND $2"
        result = await self.db.execute(query, start_date, end_date)
        # 解析结果，格式类似 "DELETE 10"
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def list_trltr(self, limit: int = 100, offset: int = 0) -> List[UsTrltrData]:
        """
        List US Treasury Real Long-term Rates records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[UsTrltrData]: List of real long-term treasury rates data
        """
        query = "SELECT * FROM us_trltr ORDER BY date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [UsTrltrData(**row) for row in rows]
    
    async def get_date_range(self) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Get the earliest and latest dates in the US Treasury Real Long-term Rates records.
        
        Returns:
            Tuple[datetime.date, datetime.date]: Tuple of (earliest_date, latest_date)
        """
        query = """
            SELECT 
                MIN(date) AS earliest_date,
                MAX(date) AS latest_date
            FROM us_trltr
        """
        row = await self.db.fetchrow(query)
        return (row['earliest_date'], row['latest_date']) if row else (None, None)
    
    async def get_latest_trltr(self) -> Optional[UsTrltrData]:
        """
        Get the latest US Treasury Real Long-term Rates record.
        
        Returns:
            UsTrltrData | None: The latest real long-term treasury rates data if available, None otherwise
        """
        query = "SELECT * FROM us_trltr ORDER BY date DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return UsTrltrData(**row) if row else None
    
    async def get_count(self) -> int:
        """
        Get the total count of US Treasury Real Long-term Rates records.
        
        Returns:
            int: Count of records
        """
        query = "SELECT COUNT(*) FROM us_trltr"
        result = await self.db.fetchval(query)
        return result
    
    async def get_ltr_avg_history(self, start_date: datetime.date, end_date: datetime.date) -> List[Dict[str, Any]]:
        """
        Get historical data for LT Real Average rates.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[Dict[str, Any]]: List of date and rate pairs
        """
        query = """
            SELECT date, ltr_avg
            FROM us_trltr 
            WHERE date BETWEEN $1 AND $2
            AND ltr_avg IS NOT NULL
            ORDER BY date
        """
        
        rows = await self.db.fetch(query, start_date, end_date)
        return [{'date': row['date'], 'ltr_avg': row['ltr_avg']} for row in rows]
    
    async def get_monthly_average(self, year: int, month: int) -> Optional[float]:
        """
        Calculate monthly average LT Real Average rate for a specific year and month.
        
        Args:
            year (int): Year
            month (int): Month (1-12)
            
        Returns:
            float | None: Monthly average LT Real Average rate or None if no data
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
                AVG(ltr_avg) AS avg_rate,
                COUNT(*) AS data_count
            FROM us_trltr
            WHERE date BETWEEN $1 AND $2
            AND ltr_avg IS NOT NULL
        """
        
        row = await self.db.fetchrow(query, start_date, end_date)
        
        if row and row['data_count'] > 0:
            return row['avg_rate']
        return None
    
    async def get_yearly_average(self, year: int) -> Optional[float]:
        """
        Calculate yearly average LT Real Average rate for a specific year.
        
        Args:
            year (int): Year
            
        Returns:
            float | None: Yearly average LT Real Average rate or None if no data
        """
        # 构建年份的开始和结束日期
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        
        query = """
            SELECT 
                AVG(ltr_avg) AS avg_rate,
                COUNT(*) AS data_count
            FROM us_trltr
            WHERE date BETWEEN $1 AND $2
            AND ltr_avg IS NOT NULL
        """
        
        row = await self.db.fetchrow(query, start_date, end_date)
        
        if row and row['data_count'] > 0:
            return row['avg_rate']
        return None
    
    async def get_moving_average(self, end_date: datetime.date, days: int = 30) -> Optional[float]:
        """
        Calculate moving average LT Real Average rate for a specific period.
        
        Args:
            end_date (datetime.date): End date of the period
            days (int): Number of days to include in the moving average
            
        Returns:
            float | None: Moving average LT Real Average rate or None if no data
        """
        # 计算开始日期
        start_date = end_date - datetime.timedelta(days=days-1)
        
        query = """
            SELECT 
                AVG(ltr_avg) AS avg_rate,
                COUNT(*) AS data_count
            FROM us_trltr
            WHERE date BETWEEN $1 AND $2
            AND ltr_avg IS NOT NULL
        """
        
        row = await self.db.fetchrow(query, start_date, end_date)
        
        if row and row['data_count'] > 0:
            return row['avg_rate']
        return None