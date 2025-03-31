import datetime
from typing import List, Optional, Tuple
from app.data.db_modules.macroeconomics_modules.cn.hibor import HiborData


class HiborCRUD:
    """
    CRUD operations for HIBOR (Hong Kong Interbank Offered Rate) data.
    
    Provides methods to create, read, update, and delete HIBOR records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_hibor(self, data: HiborData) -> None:
        """
        Create a new HIBOR record in the database.
        
        Args:
            data (HiborData): The HIBOR data to insert
        """
        query = """
            INSERT INTO hibor (
                date, on_rate, w1_rate, w2_rate, m1_rate, m2_rate, 
                m3_rate, m6_rate, m12_rate
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_hibor_by_date(self, date: datetime.date) -> Optional[HiborData]:
        """
        Retrieve a HIBOR record by date.
        
        Args:
            date (datetime.date): The date of the HIBOR to retrieve
            
        Returns:
            HiborData | None: The HIBOR data if found, None otherwise
        """
        query = "SELECT * FROM hibor WHERE date = $1"
        row = await self.db.fetchrow(query, date)
        return HiborData(**row) if row else None
    
    async def get_hibor_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[HiborData]:
        """
        Retrieve HIBOR records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[HiborData]: List of HIBOR data for the date range
        """
        query = """
            SELECT * FROM hibor 
            WHERE date BETWEEN $1 AND $2
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [HiborData(**row) for row in rows]
    
    async def update_hibor(self, date: datetime.date, updates: dict) -> None:
        """
        Update a HIBOR record by date.
        
        Args:
            date (datetime.date): The date of the HIBOR to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE hibor
            SET {set_values}
            WHERE date = $1
        """
        await self.db.execute(query, date, *updates.values())
    
    async def delete_hibor(self, date: datetime.date) -> None:
        """
        Delete a HIBOR record by date.
        
        Args:
            date (datetime.date): The date of the HIBOR to delete
        """
        query = "DELETE FROM hibor WHERE date = $1"
        await self.db.execute(query, date)
    
    async def delete_hibor_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Delete HIBOR records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM hibor WHERE date BETWEEN $1 AND $2"
        result = await self.db.execute(query, start_date, end_date)
        # 解析结果，格式类似 "DELETE 10"
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def list_hibor(self, limit: int = 100, offset: int = 0) -> List[HiborData]:
        """
        List HIBOR records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[HiborData]: List of HIBOR data
        """
        query = "SELECT * FROM hibor ORDER BY date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [HiborData(**row) for row in rows]
    
    async def get_date_range(self) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Get the earliest and latest dates in the HIBOR records.
        
        Returns:
            Tuple[datetime.date, datetime.date]: Tuple of (earliest_date, latest_date)
        """
        query = """
            SELECT 
                MIN(date) AS earliest_date,
                MAX(date) AS latest_date
            FROM hibor
        """
        row = await self.db.fetchrow(query)
        return (row['earliest_date'], row['latest_date']) if row else (None, None)
    
    async def get_latest_hibor(self) -> Optional[HiborData]:
        """
        Get the latest HIBOR record.
        
        Returns:
            HiborData | None: The latest HIBOR data if available, None otherwise
        """
        query = "SELECT * FROM hibor ORDER BY date DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return HiborData(**row) if row else None
    
    async def get_count(self) -> int:
        """
        Get the total count of HIBOR records.
        
        Returns:
            int: Count of records
        """
        query = "SELECT COUNT(*) FROM hibor"
        result = await self.db.fetchval(query)
        return result
    
    async def get_monthly_average(self, year: int, month: int) -> Optional[dict]:
        """
        Calculate monthly average HIBOR rates for a specific year and month.
        
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
                AVG(on_rate) AS avg_on_rate,
                AVG(w1_rate) AS avg_w1_rate,
                AVG(w2_rate) AS avg_w2_rate,
                AVG(m1_rate) AS avg_m1_rate,
                AVG(m2_rate) AS avg_m2_rate,
                AVG(m3_rate) AS avg_m3_rate,
                AVG(m6_rate) AS avg_m6_rate,
                AVG(m12_rate) AS avg_m12_rate,
                COUNT(*) AS data_count
            FROM hibor
            WHERE date BETWEEN $1 AND $2
        """
        
        row = await self.db.fetchrow(query, start_date, end_date)
        
        if row and row['data_count'] > 0:
            return {
                'year': year,
                'month': month,
                'on_rate': row['avg_on_rate'],
                'w1_rate': row['avg_w1_rate'],
                'w2_rate': row['avg_w2_rate'],
                'm1_rate': row['avg_m1_rate'],
                'm2_rate': row['avg_m2_rate'],
                'm3_rate': row['avg_m3_rate'],
                'm6_rate': row['avg_m6_rate'],
                'm12_rate': row['avg_m12_rate'],
                'days_count': row['data_count']
            }
        return None