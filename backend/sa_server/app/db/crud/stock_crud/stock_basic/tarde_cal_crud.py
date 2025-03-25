import datetime
from typing import List, Optional
from app.data.db_modules.stock_modules.stock_basic.tarde_cal import TradeCalData


class TradeCalCRUD:
    """
    CRUD operations for trading calendar data.
    
    Provides methods to create, read, update, and delete trading calendar records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_calendar(self, data: TradeCalData) -> None:
        """
        Create a new trading calendar record in the database.
        
        Args:
            data (TradeCalData): The calendar data to insert
        """
        query = """
            INSERT INTO tarde_cal (
                exchange, cal_date, is_open, pretrade_date
            ) VALUES (
                $1, $2, $3, $4
            )
        """
        values = [
            data.exchange,
            data.cal_date,
            data.is_open,
            data.pretrade_date
        ]
        await self.db.execute(query, *values)

    async def get_calendar(self, exchange: str, cal_date: datetime.date) -> Optional[TradeCalData]:
        """
        Retrieve a trading calendar record by its primary key.
        
        Args:
            exchange (str): Exchange code
            cal_date (datetime.date): Calendar date
            
        Returns:
            TradeCalData | None: The calendar data if found, None otherwise
        """
        query = "SELECT * FROM tarde_cal WHERE exchange = $1 AND cal_date = $2"
        row = await self.db.fetchrow(query, exchange, cal_date)
        return TradeCalData(**row) if row else None
    
    async def update_calendar(self, exchange: str, cal_date: datetime.date, updates: dict) -> None:
        """
        Update a trading calendar record by its primary key.
        
        Args:
            exchange (str): Exchange code
            cal_date (datetime.date): Calendar date
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 3}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE tarde_cal
            SET {set_values}
            WHERE exchange = $1 AND cal_date = $2
        """
        await self.db.execute(query, exchange, cal_date, *updates.values())
    
    async def delete_calendar(self, exchange: str, cal_date: datetime.date) -> None:
        """
        Delete a trading calendar record by its primary key.
        
        Args:
            exchange (str): Exchange code
            cal_date (datetime.date): Calendar date
        """
        query = "DELETE FROM tarde_cal WHERE exchange = $1 AND cal_date = $2"
        await self.db.execute(query, exchange, cal_date)
    
    async def list_calendars_by_exchange(self, exchange: str, start_date: Optional[datetime.date] = None, 
                                      end_date: Optional[datetime.date] = None, limit: int = 100) -> List[TradeCalData]:
        """
        List trading calendar records for a specific exchange within a date range.
        
        Args:
            exchange (str): Exchange code to filter by
            start_date (datetime.date, optional): Start date of the range
            end_date (datetime.date, optional): End date of the range
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[TradeCalData]: List of calendar data
        """
        params = [exchange]
        query = "SELECT * FROM tarde_cal WHERE exchange = $1"
        
        if start_date:
            params.append(start_date)
            query += f" AND cal_date >= ${len(params)}"
            
        if end_date:
            params.append(end_date)
            query += f" AND cal_date <= ${len(params)}"
            
        query += " ORDER BY cal_date LIMIT $" + str(len(params) + 1)
        params.append(limit)
        
        rows = await self.db.fetch(query, *params)
        return [TradeCalData(**row) for row in rows]
    
    async def get_trading_days(self, exchange: str, start_date: datetime.date, 
                            end_date: datetime.date) -> List[TradeCalData]:
        """
        Get all trading days within a date range.
        
        Args:
            exchange (str): Exchange code
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range
            
        Returns:
            list[TradeCalData]: List of trading day records
        """
        query = """
            SELECT * FROM tarde_cal 
            WHERE exchange = $1 AND cal_date BETWEEN $2 AND $3 AND is_open = 1
            ORDER BY cal_date
        """
        rows = await self.db.fetch(query, exchange, start_date, end_date)
        return [TradeCalData(**row) for row in rows]
    
    async def get_previous_trading_day(self, exchange: str, cal_date: datetime.date) -> Optional[TradeCalData]:
        """
        Get the previous trading day before the given date.
        
        Args:
            exchange (str): Exchange code
            cal_date (datetime.date): Reference date
            
        Returns:
            TradeCalData | None: The previous trading day data if found, None otherwise
        """
        query = """
            SELECT * FROM tarde_cal 
            WHERE exchange = $1 AND cal_date < $2 AND is_open = 1
            ORDER BY cal_date DESC 
            LIMIT 1
        """
        row = await self.db.fetchrow(query, exchange, cal_date)
        return TradeCalData(**row) if row else None
    
    async def get_next_trading_day(self, exchange: str, cal_date: datetime.date) -> Optional[TradeCalData]:
        """
        Get the next trading day after the given date.
        
        Args:
            exchange (str): Exchange code
            cal_date (datetime.date): Reference date
            
        Returns:
            TradeCalData | None: The next trading day data if found, None otherwise
        """
        query = """
            SELECT * FROM tarde_cal 
            WHERE exchange = $1 AND cal_date > $2 AND is_open = 1
            ORDER BY cal_date 
            LIMIT 1
        """
        row = await self.db.fetchrow(query, exchange, cal_date)
        return TradeCalData(**row) if row else None
    
    async def is_trading_day(self, exchange: str, cal_date: datetime.date) -> bool:
        """
        Check if a date is a trading day.
        
        Args:
            exchange (str): Exchange code
            cal_date (datetime.date): Date to check
            
        Returns:
            bool: True if it's a trading day, False otherwise
        """
        query = """
            SELECT is_open FROM tarde_cal 
            WHERE exchange = $1 AND cal_date = $2
        """
        result = await self.db.fetchval(query, exchange, cal_date)
        return result == '1' if result is not None else False