import datetime
import json
from typing import List, Optional, Tuple, Dict, Any
from app.data.db_modules.macroeconomics_modules.us.us_tycr import UsTycrData


class UsTycrCRUD:
    """
    CRUD operations for US Treasury Yield Curve Rate data.
    
    Provides methods to create, read, update, and delete yield curve records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_tycr(self, data: UsTycrData) -> None:
        """
        Create a new US Treasury yield curve record in the database.
        
        Args:
            data (UsTycrData): The yield curve data to insert
        """
        query = """
            INSERT INTO us_tycr (
                date, m1, m2, m3, m4, m6, y1, y2, y3, y5, y7, y10, y20, y30
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_tycr_by_date(self, date: datetime.date) -> Optional[UsTycrData]:
        """
        Retrieve a US Treasury yield curve record by date.
        
        Args:
            date (datetime.date): The date of the yield curve to retrieve
            
        Returns:
            UsTycrData | None: The yield curve data if found, None otherwise
        """
        query = "SELECT * FROM us_tycr WHERE date = $1"
        row = await self.db.fetchrow(query, date)
        return UsTycrData(**row) if row else None
    
    async def get_tycr_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[UsTycrData]:
        """
        Retrieve US Treasury yield curve records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[UsTycrData]: List of yield curve data for the date range
        """
        query = """
            SELECT * FROM us_tycr 
            WHERE date BETWEEN $1 AND $2
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [UsTycrData(**row) for row in rows]
    
    async def get_tycr_by_fields(self, date: datetime.date, fields: List[str]) -> Optional[Dict[str, Any]]:
        """
        Retrieve specific fields of a US Treasury yield curve record by date.
        
        Args:
            date (datetime.date): The date of the yield curve to retrieve
            fields (List[str]): List of field names to retrieve
            
        Returns:
            Dict[str, Any] | None: Dictionary with selected fields if found, None otherwise
        """
        # 验证字段名
        valid_fields = {
            'm1', 'm2', 'm3', 'm4', 'm6', 
            'y1', 'y2', 'y3', 'y5', 'y7', 'y10', 'y20', 'y30'
        }
        
        selected_fields = ['date']
        for field in fields:
            if field in valid_fields:
                selected_fields.append(field)
        
        # 如果没有有效字段，返回None
        if len(selected_fields) <= 1:
            return None
        
        # 构建查询
        selected_cols = ', '.join(selected_fields)
        query = f"SELECT {selected_cols} FROM us_tycr WHERE date = $1"
        
        row = await self.db.fetchrow(query, date)
        return dict(row) if row else None
    
    async def update_tycr(self, date: datetime.date, updates: dict) -> None:
        """
        Update a US Treasury yield curve record by date.
        
        Args:
            date (datetime.date): The date of the yield curve to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE us_tycr
            SET {set_values}
            WHERE date = $1
        """
        await self.db.execute(query, date, *updates.values())
    
    async def delete_tycr(self, date: datetime.date) -> None:
        """
        Delete a US Treasury yield curve record by date.
        
        Args:
            date (datetime.date): The date of the yield curve to delete
        """
        query = "DELETE FROM us_tycr WHERE date = $1"
        await self.db.execute(query, date)
    
    async def delete_tycr_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Delete US Treasury yield curve records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM us_tycr WHERE date BETWEEN $1 AND $2"
        result = await self.db.execute(query, start_date, end_date)
        # 解析结果，格式类似 "DELETE 10"
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def list_tycr(self, limit: int = 100, offset: int = 0) -> List[UsTycrData]:
        """
        List US Treasury yield curve records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[UsTycrData]: List of yield curve data
        """
        query = "SELECT * FROM us_tycr ORDER BY date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [UsTycrData(**row) for row in rows]
    
    async def get_date_range(self) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Get the earliest and latest dates in the US Treasury yield curve records.
        
        Returns:
            Tuple[datetime.date, datetime.date]: Tuple of (earliest_date, latest_date)
        """
        query = """
            SELECT 
                MIN(date) AS earliest_date,
                MAX(date) AS latest_date
            FROM us_tycr
        """
        row = await self.db.fetchrow(query)
        return (row['earliest_date'], row['latest_date']) if row else (None, None)
    
    async def get_latest_tycr(self) -> Optional[UsTycrData]:
        """
        Get the latest US Treasury yield curve record.
        
        Returns:
            UsTycrData | None: The latest yield curve data if available, None otherwise
        """
        query = "SELECT * FROM us_tycr ORDER BY date DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return UsTycrData(**row) if row else None
    
    async def get_count(self) -> int:
        """
        Get the total count of US Treasury yield curve records.
        
        Returns:
            int: Count of records
        """
        query = "SELECT COUNT(*) FROM us_tycr"
        result = await self.db.fetchval(query)
        return result
    
    async def get_yield_spread(self, date: datetime.date, term1: str, term2: str) -> Optional[float]:
        """
        Calculate the yield spread between two terms for a specific date.
        
        Args:
            date (datetime.date): The date to calculate spread for
            term1 (str): First term (e.g., 'y10')
            term2 (str): Second term (e.g., 'y2')
            
        Returns:
            float | None: The yield spread (term1 - term2) if both rates are available, None otherwise
        """
        valid_terms = {
            'm1', 'm2', 'm3', 'm4', 'm6', 
            'y1', 'y2', 'y3', 'y5', 'y7', 'y10', 'y20', 'y30'
        }
        
        if term1 not in valid_terms or term2 not in valid_terms:
            raise ValueError(f"无效的期限参数，必须是以下之一: {valid_terms}")
        
        query = f"SELECT {term1}, {term2} FROM us_tycr WHERE date = $1"
        row = await self.db.fetchrow(query, date)
        
        if row and row[term1] is not None and row[term2] is not None:
            return row[term1] - row[term2]
        return None
    
    async def get_yield_spread_history(self, start_date: datetime.date, end_date: datetime.date, 
                                      term1: str, term2: str) -> List[Dict[str, Any]]:
        """
        Calculate the yield spread history between two terms for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            term1 (str): First term (e.g., 'y10')
            term2 (str): Second term (e.g., 'y2')
            
        Returns:
            List[Dict[str, Any]]: List of date and spread pairs
        """
        valid_terms = {
            'm1', 'm2', 'm3', 'm4', 'm6', 
            'y1', 'y2', 'y3', 'y5', 'y7', 'y10', 'y20', 'y30'
        }
        
        if term1 not in valid_terms or term2 not in valid_terms:
            raise ValueError(f"无效的期限参数，必须是以下之一: {valid_terms}")
        
        query = f"""
            SELECT date, {term1}, {term2}, ({term1} - {term2}) AS spread
            FROM us_tycr 
            WHERE date BETWEEN $1 AND $2
            AND {term1} IS NOT NULL AND {term2} IS NOT NULL
            ORDER BY date
        """
        
        rows = await self.db.fetch(query, start_date, end_date)
        return [
            {
                'date': row['date'],
                'spread': row['spread'],
                term1: row[term1],
                term2: row[term2]
            } 
            for row in rows
        ]
    
    async def get_yield_curve_snapshot(self, date: datetime.date) -> Optional[Dict[str, Any]]:
        """
        Get a snapshot of the full yield curve for a specific date.
        
        Args:
            date (datetime.date): The date to get snapshot for
            
        Returns:
            Dict[str, Any] | None: Dictionary with term and rate pairs if found, None otherwise
        """
        query = """
            SELECT 
                date, m1, m2, m3, m4, m6, y1, y2, y3, y5, y7, y10, y20, y30
            FROM us_tycr 
            WHERE date = $1
        """
        
        row = await self.db.fetchrow(query, date)
        return dict(row) if row else None
    
    async def get_term_history(self, term: str, start_date: datetime.date, 
                             end_date: datetime.date) -> List[Dict[str, Any]]:
        """
        Get historical data for a specific term over a date range.
        
        Args:
            term (str): Term to get history for (e.g., 'y10')
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[Dict[str, Any]]: List of date and rate pairs
        """
        valid_terms = {
            'm1', 'm2', 'm3', 'm4', 'm6', 
            'y1', 'y2', 'y3', 'y5', 'y7', 'y10', 'y20', 'y30'
        }
        
        if term not in valid_terms:
            raise ValueError(f"无效的期限参数，必须是以下之一: {valid_terms}")
        
        query = f"""
            SELECT date, {term}
            FROM us_tycr 
            WHERE date BETWEEN $1 AND $2
            AND {term} IS NOT NULL
            ORDER BY date
        """
        
        rows = await self.db.fetch(query, start_date, end_date)
        return [{'date': row['date'], 'rate': row[term]} for row in rows]