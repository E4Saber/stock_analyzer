import datetime
from typing import List, Optional, Tuple, Dict, Any
from app.data.db_modules.macroeconomics_modules.us.us_tbr import UsTbrData


class UsTbrCRUD:
    """
    CRUD operations for US Treasury Bill Rates data.
    
    Provides methods to create, read, update, and delete treasury bill rates records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_tbr(self, data: UsTbrData) -> None:
        """
        Create a new US Treasury Bill Rates record in the database.
        
        Args:
            data (UsTbrData): The treasury bill rates data to insert
        """
        query = """
            INSERT INTO us_tbr (
                date, w4_bd, w4_ce, w8_bd, w8_ce, w13_bd, w13_ce,
                w17_bd, w17_ce, w26_bd, w26_ce, w52_bd, w52_ce
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_tbr_by_date(self, date: datetime.date) -> Optional[UsTbrData]:
        """
        Retrieve a US Treasury Bill Rates record by date.
        
        Args:
            date (datetime.date): The date of the treasury bill rates to retrieve
            
        Returns:
            UsTbrData | None: The treasury bill rates data if found, None otherwise
        """
        query = "SELECT * FROM us_tbr WHERE date = $1"
        row = await self.db.fetchrow(query, date)
        return UsTbrData(**row) if row else None
    
    async def get_tbr_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> List[UsTbrData]:
        """
        Retrieve US Treasury Bill Rates records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[UsTbrData]: List of treasury bill rates data for the date range
        """
        query = """
            SELECT * FROM us_tbr 
            WHERE date BETWEEN $1 AND $2
            ORDER BY date
        """
        rows = await self.db.fetch(query, start_date, end_date)
        return [UsTbrData(**row) for row in rows]
    
    async def get_tbr_by_fields(self, date: datetime.date, fields: List[str]) -> Optional[Dict[str, Any]]:
        """
        Retrieve specific fields of a US Treasury Bill Rates record by date.
        
        Args:
            date (datetime.date): The date of the treasury bill rates to retrieve
            fields (List[str]): List of field names to retrieve
            
        Returns:
            Dict[str, Any] | None: Dictionary with selected fields if found, None otherwise
        """
        # 验证字段名
        valid_fields = {
            'w4_bd', 'w4_ce', 'w8_bd', 'w8_ce', 'w13_bd', 'w13_ce',
            'w17_bd', 'w17_ce', 'w26_bd', 'w26_ce', 'w52_bd', 'w52_ce'
        }
        
        selected_fields = ['date']
        for field in fields:
            if field in valid_fields:
                selected_fields.append(field)
        
        # a如果没有有效字段，返回None
        if len(selected_fields) <= 1:
            return None
        
        # 构建查询
        selected_cols = ', '.join(selected_fields)
        query = f"SELECT {selected_cols} FROM us_tbr WHERE date = $1"
        
        row = await self.db.fetchrow(query, date)
        return dict(row) if row else None
    
    async def update_tbr(self, date: datetime.date, updates: dict) -> None:
        """
        Update a US Treasury Bill Rates record by date.
        
        Args:
            date (datetime.date): The date of the treasury bill rates to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE us_tbr
            SET {set_values}
            WHERE date = $1
        """
        await self.db.execute(query, date, *updates.values())
    
    async def delete_tbr(self, date: datetime.date) -> None:
        """
        Delete a US Treasury Bill Rates record by date.
        
        Args:
            date (datetime.date): The date of the treasury bill rates to delete
        """
        query = "DELETE FROM us_tbr WHERE date = $1"
        await self.db.execute(query, date)
    
    async def delete_tbr_by_date_range(self, start_date: datetime.date, end_date: datetime.date) -> int:
        """
        Delete US Treasury Bill Rates records for a date range.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM us_tbr WHERE date BETWEEN $1 AND $2"
        result = await self.db.execute(query, start_date, end_date)
        # 解析结果，格式类似 "DELETE 10"
        try:
            return int(result.split()[1])
        except (IndexError, ValueError):
            return 0
    
    async def list_tbr(self, limit: int = 100, offset: int = 0) -> List[UsTbrData]:
        """
        List US Treasury Bill Rates records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            List[UsTbrData]: List of treasury bill rates data
        """
        query = "SELECT * FROM us_tbr ORDER BY date DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [UsTbrData(**row) for row in rows]
    
    async def get_date_range(self) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        """
        Get the earliest and latest dates in the US Treasury Bill Rates records.
        
        Returns:
            Tuple[datetime.date, datetime.date]: Tuple of (earliest_date, latest_date)
        """
        query = """
            SELECT 
                MIN(date) AS earliest_date,
                MAX(date) AS latest_date
            FROM us_tbr
        """
        row = await self.db.fetchrow(query)
        return (row['earliest_date'], row['latest_date']) if row else (None, None)
    
    async def get_latest_tbr(self) -> Optional[UsTbrData]:
        """
        Get the latest US Treasury Bill Rates record.
        
        Returns:
            UsTbrData | None: The latest treasury bill rates data if available, None otherwise
        """
        query = "SELECT * FROM us_tbr ORDER BY date DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return UsTbrData(**row) if row else None
    
    async def get_count(self) -> int:
        """
        Get the total count of US Treasury Bill Rates records.
        
        Returns:
            int: Count of records
        """
        query = "SELECT COUNT(*) FROM us_tbr"
        result = await self.db.fetchval(query)
        return result
    
    async def get_spread_by_term(self, date: datetime.date, term: str) -> Optional[float]:
        """
        Calculate the spread between coupon equivalent rate and bank discount rate for a specific term.
        
        Args:
            date (datetime.date): The date to calculate spread for
            term (str): Term (e.g., 'w4', 'w13', 'w52')
            
        Returns:
            float | None: The spread (ce - bd) if both rates are available, None otherwise
        """
        valid_terms = {'w4', 'w8', 'w13', 'w17', 'w26', 'w52'}
        
        if term not in valid_terms:
            raise ValueError(f"无效的期限参数，必须是以下之一: {valid_terms}")
        
        bd_field = f"{term}_bd"
        ce_field = f"{term}_ce"
        
        query = f"SELECT {bd_field}, {ce_field} FROM us_tbr WHERE date = $1"
        row = await self.db.fetchrow(query, date)
        
        if row and row[bd_field] is not None and row[ce_field] is not None:
            return row[ce_field] - row[bd_field]
        return None
    
    async def get_spread_history_by_term(self, start_date: datetime.date, end_date: datetime.date, 
                                        term: str) -> List[Dict[str, Any]]:
        """
        Calculate the spread history between coupon equivalent rate and bank discount rate for a specific term.
        
        Args:
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            term (str): Term (e.g., 'w4', 'w13', 'w52')
            
        Returns:
            List[Dict[str, Any]]: List of date and spread pairs
        """
        valid_terms = {'w4', 'w8', 'w13', 'w17', 'w26', 'w52'}
        
        if term not in valid_terms:
            raise ValueError(f"无效的期限参数，必须是以下之一: {valid_terms}")
        
        bd_field = f"{term}_bd"
        ce_field = f"{term}_ce"
        
        query = f"""
            SELECT date, {bd_field}, {ce_field}, ({ce_field} - {bd_field}) AS spread
            FROM us_tbr 
            WHERE date BETWEEN $1 AND $2
            AND {bd_field} IS NOT NULL AND {ce_field} IS NOT NULL
            ORDER BY date
        """
        
        rows = await self.db.fetch(query, start_date, end_date)
        return [
            {
                'date': row['date'],
                'spread': row['spread'],
                'bd_rate': row[bd_field],
                'ce_rate': row[ce_field]
            } 
            for row in rows
        ]
    
    async def get_rates_by_term(self, term: str, start_date: datetime.date, 
                               end_date: datetime.date) -> List[Dict[str, Any]]:
        """
        Get historical data for a specific term over a date range.
        
        Args:
            term (str): Term to get history for (e.g., 'w4', 'w13', 'w52')
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            List[Dict[str, Any]]: List with date, bank discount rate, and coupon equivalent rate
        """
        valid_terms = {'w4', 'w8', 'w13', 'w17', 'w26', 'w52'}
        
        if term not in valid_terms:
            raise ValueError(f"无效的期限参数，必须是以下之一: {valid_terms}")
        
        bd_field = f"{term}_bd"
        ce_field = f"{term}_ce"
        
        query = f"""
            SELECT date, {bd_field}, {ce_field}
            FROM us_tbr 
            WHERE date BETWEEN $1 AND $2
            AND ({bd_field} IS NOT NULL OR {ce_field} IS NOT NULL)
            ORDER BY date
        """
        
        rows = await self.db.fetch(query, start_date, end_date)
        return [
            {
                'date': row['date'],
                'bd_rate': row[bd_field],
                'ce_rate': row[ce_field]
            } 
            for row in rows
        ]
    
    async def get_term_comparison(self, date: datetime.date, 
                                 terms: List[str], 
                                 rate_type: str = 'bd') -> Optional[Dict[str, Any]]:
        """
        Compare rates across different terms for a specific date.
        
        Args:
            date (datetime.date): The date to compare rates for
            terms (List[str]): List of terms to compare (e.g., ['w4', 'w13', 'w52'])
            rate_type (str): Rate type to compare ('bd' for bank discount rate or 'ce' for coupon equivalent rate)
            
        Returns:
            Dict[str, Any] | None: Dictionary with term and rate pairs if found, None otherwise
        """
        valid_terms = {'w4', 'w8', 'w13', 'w17', 'w26', 'w52'}
        valid_rate_types = {'bd', 'ce'}
        
        if rate_type not in valid_rate_types:
            raise ValueError(f"无效的利率类型，必须是 'bd' 或 'ce'")
        
        filtered_terms = [term for term in terms if term in valid_terms]
        
        if not filtered_terms:
            return None
        
        fields = [f"{term}_{rate_type}" for term in filtered_terms]
        fields_str = ', '.join(fields)
        
        query = f"SELECT date, {fields_str} FROM us_tbr WHERE date = $1"
        
        row = await self.db.fetchrow(query, date)
        
        if row:
            result = {'date': row['date']}
            for term in filtered_terms:
                field = f"{term}_{rate_type}"
                result[term] = row[field]
            return result
        return None