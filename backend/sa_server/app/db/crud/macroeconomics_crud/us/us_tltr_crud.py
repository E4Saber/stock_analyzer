import datetime
from typing import List, Optional, Tuple, Dict, Any
from app.data.db_modules.macroeconomics_modules.us.us_tltr import UsTltrData


class UsTltrCRUD:
    """
    CRUD operations for US Treasury Long-term Rates data.
    
    Provides methods to create, read, update, and delete long-term treasury rates records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_tltr(self, data: UsTltrData) -> None:
        """
        Create a new US Treasury Long-term Rates record in the database.
        
        Args:
            data (UsTltrData): The long-term treasury rates data to insert
        """
        query = """
            INSERT INTO us_tltr (
                date, ltc, cmt, e_factor
            ) VALUES (
                $1, $2, $3, $4
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_tltr_by_date(self, date: datetime.date) -> Optional[UsTltrData]:
        """
        Retrieve a US Treasury Long-term Rates record by date.
        
        Args:
            date (datetime.date): The date of the long-term treasury rates to retrieve
            
        Returns:
            UsTltrData | None: The long-term treasury rates data if found, None otherwise
        """
        query = "SELECT * FROM us_tltr WHERE date = $1"
        row = await self.db.fetchrow(query, date)
        return UsTltrData(**row) if row else None
    
    async def get_tltr_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[UsTltrData]:
        """
        Retrieve US Treasury Long-term Rates records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[UsTltrData]: List of long-term treasury rates data for the date range
        """
        query = """
            SELECT * FROM us_tltr 
            WHERE date BETWEEN $1 AND $2
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [UsTltrData(**row) for row in rows]
    
    async def get_tltr_by_fields(self, date: datetime.date, fields: List[str]) -> Optional[Dict[str, Any]]:
        """
        Retrieve specific fields of a US Treasury Long-term Rates record by date.
        
        Args:
            date (datetime.date): The date of the long-term treasury rates to retrieve
            fields (List[str]): List of field names to retrieve
            
        Returns:
            Dict[str, Any] | None: Dictionary with selected fields if found, None otherwise
        """
        # 验证字段名
        valid_fields = {'ltc', 'cmt', 'e_factor'}
        
        selected_fields = ['date']
        for field in fields:
            if field in valid_fields:
                selected_fields.append(field)
        
        # 如果没有有效字段，返回None
        if len(selected_fields) <= 1:
            return None
        
        # 构建查询
        selected_cols = ', '.join(selected_fields)
        query = f"SELECT {selected_cols} FROM us_tltr WHERE date = $1"
        
        row = await self.db.fetchrow(query, date)
        return dict(row) if row else None
    
    async def update_tltr(self, date: datetime.date, updates: dict) -> None:
        """
        Update a US Treasury Long-term Rates record by date.
        
        Args:
            date (datetime.date): The date of the long-term treasury rates to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE us_tltr
            SET {set_values}
            WHERE date = $1
        """
        await self.db.execute(query, date, *updates.values())
    
    async def delete_tltr(self, date: datetime.date) -> None:
        """
        Delete a US Treasury Long-term Rates record by date.
        
        Args:
            date (datetime.date): The date of the long-term treasury rates to delete
        """
        query = "DELETE FROM us_tltr WHERE date = $1"
        await self.db.execute(query, date)
    
    async def delete_tltr_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Delete US Treasury Long-term Rates records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM us_tltr WHERE date BETWEEN $1 AND $2"
        result = await self.db.execute(query, start_date, end_date)
        # 解析结果，格式类似 "DELETE 10"
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def list_tltr(self, limit: int = 100, offset: int = 0) -> List[UsTltrData]:
        """
        List US Treasury Long-term Rates records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[UsTltrData]: List of long-term treasury rates data
        """
        query = "SELECT * FROM us_tltr ORDER BY date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [UsTltrData(**row) for row in rows]
    
    async def get_date_range(self) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Get the earliest and latest dates in the US Treasury Long-term Rates records.
        
        Returns:
            Tuple[datetime.date, datetime.date]: Tuple of (earliest_date, latest_date)
        """
        query = """
            SELECT 
                MIN(date) AS earliest_date,
                MAX(date) AS latest_date
            FROM us_tltr
        """
        row = await self.db.fetchrow(query)
        return (row['earliest_date'], row['latest_date']) if row else (None, None)
    
    async def get_latest_tltr(self) -> Optional[UsTltrData]:
        """
        Get the latest US Treasury Long-term Rates record.
        
        Returns:
            UsTltrData | None: The latest long-term treasury rates data if available, None otherwise
        """
        query = "SELECT * FROM us_tltr ORDER BY date DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return UsTltrData(**row) if row else None
    
    async def get_count(self) -> int:
        """
        Get the total count of US Treasury Long-term Rates records.
        
        Returns:
            int: Count of records
        """
        query = "SELECT COUNT(*) FROM us_tltr"
        result = await self.db.fetchval(query)
        return result
    
    async def get_ltc_history(self, start_date: datetime.date, end_date: datetime.date) -> List[Dict[str, Any]]:
        """
        Get historical data for LT COMPOSITE rates.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[Dict[str, Any]]: List of date and rate pairs
        """
        query = """
            SELECT date, ltc
            FROM us_tltr 
            WHERE date BETWEEN $1 AND $2
            AND ltc IS NOT NULL
            ORDER BY date
        """
        
        rows = await self.db.fetch(query, start_date, end_date)
        return [{'date': row['date'], 'ltc': row['ltc']} for row in rows]
    
    async def get_cmt_history(self, start_date: datetime.date, end_date: datetime.date) -> List[Dict[str, Any]]:
        """
        Get historical data for 20-Year CMT rates.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[Dict[str, Any]]: List of date and rate pairs
        """
        query = """
            SELECT date, cmt
            FROM us_tltr 
            WHERE date BETWEEN $1 AND $2
            AND cmt IS NOT NULL
            ORDER BY date
        """
        
        rows = await self.db.fetch(query, start_date, end_date)
        return [{'date': row['date'], 'cmt': row['cmt']} for row in rows]
    
    async def get_factor_history(self, start_date: datetime.date, end_date: datetime.date) -> List[Dict[str, Any]]:
        """
        Get historical data for extrapolation factors.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[Dict[str, Any]]: List of date and factor pairs
        """
        query = """
            SELECT date, e_factor
            FROM us_tltr 
            WHERE date BETWEEN $1 AND $2
            AND e_factor IS NOT NULL
            ORDER BY date
        """
        
        rows = await self.db.fetch(query, start_date, end_date)
        return [{'date': row['date'], 'factor': row['e_factor']} for row in rows]
    
    async def get_spread_history(self, start_date: datetime.date, end_date: datetime.date) -> List[Dict[str, Any]]:
        """
        Calculate the spread history between LT COMPOSITE and 20-Year CMT rates.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[Dict[str, Any]]: List of date, rates, and spread
        """
        query = """
            SELECT date, ltc, cmt, (ltc - cmt) AS spread
            FROM us_tltr 
            WHERE date BETWEEN $1 AND $2
            AND ltc IS NOT NULL AND cmt IS NOT NULL
            ORDER BY date
        """
        
        rows = await self.db.fetch(query, start_date, end_date)
        return [
            {
                'date': row['date'],
                'ltc': row['ltc'],
                'cmt': row['cmt'],
                'spread': row['spread']
            } 
            for row in rows
        ]
    
    async def get_monthly_average(self, year: int, month: int) -> Optional[Dict[str, Any]]:
        """
        Calculate monthly average rates for a specific year and month.
        
        Args:
            year (int): Year
            month (int): Month (1-12)
            
        Returns:
            Dict[str, Any] | None: Dictionary with average rates or None if no data
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
                AVG(ltc) AS avg_ltc,
                AVG(cmt) AS avg_cmt,
                AVG(e_factor) AS avg_factor,
                COUNT(*) AS data_count
            FROM us_tltr
            WHERE date BETWEEN $1 AND $2
        """
        
        row = await self.db.fetchrow(query, start_date, end_date)
        
        if row and row['data_count'] > 0:
            return {
                'year': year,
                'month': month,
                'ltc': row['avg_ltc'],
                'cmt': row['avg_cmt'],
                'e_factor': row['avg_factor'],
                'days_count': row['data_count']
            }
        return None