import datetime
from typing import List, Optional, Tuple
from app.data.db_modules.macroeconomics_modules.cn.wz_index import WzIndexData


class WzIndexCRUD:
    """
    CRUD operations for Wenzhou Private Financing Index data.
    
    Provides methods to create, read, update, and delete index records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_index(self, data: WzIndexData) -> None:
        """
        Create a new Wenzhou index record in the database.
        
        Args:
            data (WzIndexData): The index data to insert
        """
        query = """
            INSERT INTO wz_index (
                date, comp_rate, center_rate, micro_rate, cm_rate, sdb_rate, om_rate,
                aa_rate, m1_rate, m3_rate, m6_rate, m12_rate, long_rate
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_index_by_date(self, date: datetime.date) -> Optional[WzIndexData]:
        """
        Retrieve a Wenzhou index record by date.
        
        Args:
            date (datetime.date): The date of the index to retrieve
            
        Returns:
            WzIndexData | None: The index data if found, None otherwise
        """
        query = "SELECT * FROM wz_index WHERE date = $1"
        row = await self.db.fetchrow(query, date)
        return WzIndexData(**row) if row else None
    
    async def get_indices_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[WzIndexData]:
        """
        Retrieve Wenzhou index records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[WzIndexData]: List of index data for the date range
        """
        query = """
            SELECT * FROM wz_index 
            WHERE date BETWEEN $1 AND $2
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [WzIndexData(**row) for row in rows]
    
    async def update_index(self, date: datetime.date, updates: dict) -> None:
        """
        Update a Wenzhou index record by date.
        
        Args:
            date (datetime.date): The date of the index to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE wz_index
            SET {set_values}
            WHERE date = $1
        """
        await self.db.execute(query, date, *updates.values())
    
    async def delete_index(self, date: datetime.date) -> None:
        """
        Delete a Wenzhou index record by date.
        
        Args:
            date (datetime.date): The date of the index to delete
        """
        query = "DELETE FROM wz_index WHERE date = $1"
        await self.db.execute(query, date)
    
    async def delete_indices_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Delete Wenzhou index records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM wz_index WHERE date BETWEEN $1 AND $2"
        result = await self.db.execute(query, start_date, end_date)
        # 解析结果，格式类似 "DELETE 10"
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def list_indices(self, limit: int = 100, offset: int = 0) -> List[WzIndexData]:
        """
        List Wenzhou index records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[WzIndexData]: List of index data
        """
        query = "SELECT * FROM wz_index ORDER BY date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [WzIndexData(**row) for row in rows]
    
    async def get_date_range(self) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Get the earliest and latest dates in the Wenzhou index records.
        
        Returns:
            Tuple[datetime.date, datetime.date]: Tuple of (earliest_date, latest_date)
        """
        query = """
            SELECT 
                MIN(date) AS earliest_date,
                MAX(date) AS latest_date
            FROM wz_index
        """
        row = await self.db.fetchrow(query)
        return (row['earliest_date'], row['latest_date']) if row else (None, None)
    
    async def get_latest_index(self) -> Optional[WzIndexData]:
        """
        Get the latest Wenzhou index record.
        
        Returns:
            WzIndexData | None: The latest index data if available, None otherwise
        """
        query = "SELECT * FROM wz_index ORDER BY date DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return WzIndexData(**row) if row else None
    
    async def get_count(self) -> int:
        """
        Get the total count of Wenzhou index records.
        
        Returns:
            int: Count of records
        """
        query = "SELECT COUNT(*) FROM wz_index"
        result = await self.db.fetchval(query)
        return result
    
    async def get_monthly_average(self, year: int, month: int) -> Optional[dict]:
        """
        Calculate monthly average rates for a specific year and month.
        
        Args:
            year (int): Year
            month (int): Month (1-12)
            
        Returns:
            dict | None: Dictionary with average rates for each indicator or None if no data
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
                AVG(comp_rate) AS avg_comp_rate,
                AVG(center_rate) AS avg_center_rate,
                AVG(micro_rate) AS avg_micro_rate,
                AVG(cm_rate) AS avg_cm_rate,
                AVG(sdb_rate) AS avg_sdb_rate,
                AVG(om_rate) AS avg_om_rate,
                AVG(aa_rate) AS avg_aa_rate,
                AVG(m1_rate) AS avg_m1_rate,
                AVG(m3_rate) AS avg_m3_rate,
                AVG(m6_rate) AS avg_m6_rate,
                AVG(m12_rate) AS avg_m12_rate,
                AVG(long_rate) AS avg_long_rate,
                COUNT(*) AS data_count
            FROM wz_index
            WHERE date BETWEEN $1 AND $2
        """
        
        row = await self.db.fetchrow(query, start_date, end_date)
        
        if row and row['data_count'] > 0:
            return {
                'year': year,
                'month': month,
                'comp_rate': row['avg_comp_rate'],
                'center_rate': row['avg_center_rate'],
                'micro_rate': row['avg_micro_rate'],
                'cm_rate': row['avg_cm_rate'],
                'sdb_rate': row['avg_sdb_rate'],
                'om_rate': row['avg_om_rate'],
                'aa_rate': row['avg_aa_rate'],
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
            dict | None: Dictionary with average rates for each indicator or None if no data
        """
        # 构建年份的开始和结束日期
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        
        query = """
            SELECT 
                AVG(comp_rate) AS avg_comp_rate,
                AVG(center_rate) AS avg_center_rate,
                AVG(micro_rate) AS avg_micro_rate,
                AVG(cm_rate) AS avg_cm_rate,
                AVG(sdb_rate) AS avg_sdb_rate,
                AVG(om_rate) AS avg_om_rate,
                AVG(aa_rate) AS avg_aa_rate,
                AVG(m1_rate) AS avg_m1_rate,
                AVG(m3_rate) AS avg_m3_rate,
                AVG(m6_rate) AS avg_m6_rate,
                AVG(m12_rate) AS avg_m12_rate,
                AVG(long_rate) AS avg_long_rate,
                COUNT(*) AS data_count
            FROM wz_index
            WHERE date BETWEEN $1 AND $2
        """
        
        row = await self.db.fetchrow(query, start_date, end_date)
        
        if row and row['data_count'] > 0:
            return {
                'year': year,
                'comp_rate': row['avg_comp_rate'],
                'center_rate': row['avg_center_rate'],
                'micro_rate': row['avg_micro_rate'],
                'cm_rate': row['avg_cm_rate'],
                'sdb_rate': row['avg_sdb_rate'],
                'om_rate': row['avg_om_rate'],
                'aa_rate': row['avg_aa_rate'],
                'm1_rate': row['avg_m1_rate'],
                'm3_rate': row['avg_m3_rate'],
                'm6_rate': row['avg_m6_rate'],
                'm12_rate': row['avg_m12_rate'],
                'long_rate': row['avg_long_rate'],
                'days_count': row['data_count']
            }
        return None