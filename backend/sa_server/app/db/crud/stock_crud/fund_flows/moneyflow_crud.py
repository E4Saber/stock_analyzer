from app.data.db_modules.stock_modules.moneyflow.moneyflow import MoneyflowData
from typing import List, Optional
import datetime


class MoneyflowCRUD:
    """
    CRUD operations for stock moneyflow data.
    
    Provides methods to create, read, update, and delete moneyflow records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_moneyflow(self, data: MoneyflowData) -> None:
        """
        Create a new moneyflow record in the database.
        
        Args:
            data (MoneyflowData): The moneyflow data to insert
        """
        query = """
            INSERT INTO moneyflow (
                ts_code, trade_date, buy_sm_vol, buy_sm_amount, sell_sm_vol, sell_sm_amount,
                buy_md_vol, buy_md_amount, sell_md_vol, sell_md_amount, buy_lg_vol, buy_lg_amount,
                sell_lg_vol, sell_lg_amount, buy_elg_vol, buy_elg_amount, sell_elg_vol, sell_elg_amount,
                net_mf_vol, net_mf_amount
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20
            )
        """
        await self.db.execute(query, *data.model_dump().values())

    async def get_moneyflow_by_code_and_date(self, ts_code: str, trade_date: str) -> Optional[MoneyflowData]:
        """
        Retrieve a moneyflow record by its TS code and trade date.
        
        Args:
            ts_code (str): The TS code of the stock
            trade_date (str): The trade date in 'YYYYMMDD' format
            
        Returns:
            MoneyflowData | None: The moneyflow data if found, None otherwise
        """
        query = "SELECT * FROM moneyflow WHERE ts_code = $1 AND trade_date = $2"
        
        # 解析日期字符串为日期对象
        if isinstance(trade_date, str) and len(trade_date) == 8:
            parsed_date = datetime.date(
                int(trade_date[:4]), 
                int(trade_date[4:6]), 
                int(trade_date[6:8])
            )
        else:
            parsed_date = trade_date
            
        row = await self.db.fetchrow(query, ts_code, parsed_date)
        return MoneyflowData(**row) if row else None
    
    async def get_moneyflow_by_code(self, ts_code: str, 
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None,
                                    limit: int = 100) -> List[MoneyflowData]:
        """
        Retrieve moneyflow records for a specific stock within a date range.
        
        Args:
            ts_code (str): The TS code of the stock
            start_date (str, optional): Start date in 'YYYYMMDD' format
            end_date (str, optional): End date in 'YYYYMMDD' format
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[MoneyflowData]: List of moneyflow data
        """
        params = [ts_code]
        query = "SELECT * FROM moneyflow WHERE ts_code = $1"
        
        # 添加日期范围条件
        if start_date:
            if isinstance(start_date, str) and len(start_date) == 8:
                parsed_start_date = datetime.date(
                    int(start_date[:4]), 
                    int(start_date[4:6]), 
                    int(start_date[6:8])
                )
            else:
                parsed_start_date = start_date
                
            query += f" AND trade_date >= ${len(params) + 1}"
            params.append(parsed_start_date)
            
        if end_date:
            if isinstance(end_date, str) and len(end_date) == 8:
                parsed_end_date = datetime.date(
                    int(end_date[:4]), 
                    int(end_date[4:6]), 
                    int(end_date[6:8])
                )
            else:
                parsed_end_date = end_date
                
            query += f" AND trade_date <= ${len(params) + 1}"
            params.append(parsed_end_date)
            
        query += f" ORDER BY trade_date DESC LIMIT ${len(params) + 1}"
        params.append(limit)
        
        rows = await self.db.fetch(query, *params)
        return [MoneyflowData(**row) for row in rows]
    
    async def get_moneyflow_by_date(self, trade_date: str, limit: int = 100) -> List[MoneyflowData]:
        """
        Retrieve moneyflow records for a specific date.
        
        Args:
            trade_date (str): The trade date in 'YYYYMMDD' format
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[MoneyflowData]: List of moneyflow data
        """
        # 解析日期字符串为日期对象
        if isinstance(trade_date, str) and len(trade_date) == 8:
            parsed_date = datetime.date(
                int(trade_date[:4]), 
                int(trade_date[4:6]), 
                int(trade_date[6:8])
            )
        else:
            parsed_date = trade_date
            
        query = "SELECT * FROM moneyflow WHERE trade_date = $1 ORDER BY net_mf_amount DESC LIMIT $2"
        rows = await self.db.fetch(query, parsed_date, limit)
        return [MoneyflowData(**row) for row in rows]
    
    async def update_moneyflow(self, ts_code: str, trade_date: str, updates: dict) -> None:
        """
        Update a moneyflow record.
        
        Args:
            ts_code (str): The TS code of the stock
            trade_date (str): The trade date in 'YYYYMMDD' format
            updates (dict): Dictionary of fields to update and their new values
        """
        # 解析日期字符串为日期对象
        if isinstance(trade_date, str) and len(trade_date) == 8:
            parsed_date = datetime.date(
                int(trade_date[:4]), 
                int(trade_date[4:6]), 
                int(trade_date[6:8])
            )
        else:
            parsed_date = trade_date
            
        set_values = ','.join([f"{key} = ${idx + 3}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE moneyflow
            SET {set_values}
            WHERE ts_code = $1 AND trade_date = $2
        """
        await self.db.execute(query, ts_code, parsed_date, *updates.values())
    
    async def delete_moneyflow(self, ts_code: str, trade_date: str) -> None:
        """
        Delete a moneyflow record.
        
        Args:
            ts_code (str): The TS code of the stock
            trade_date (str): The trade date in 'YYYYMMDD' format
        """
        # 解析日期字符串为日期对象
        if isinstance(trade_date, str) and len(trade_date) == 8:
            parsed_date = datetime.date(
                int(trade_date[:4]), 
                int(trade_date[4:6]), 
                int(trade_date[6:8])
            )
        else:
            parsed_date = trade_date
            
        query = "DELETE FROM moneyflow WHERE ts_code = $1 AND trade_date = $2"
        await self.db.execute(query, ts_code, parsed_date)
    
    async def delete_moneyflow_by_code(self, ts_code: str) -> int:
        """
        Delete all moneyflow records for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM moneyflow WHERE ts_code = $1"
        result = await self.db.execute(query, ts_code)
        
        # 解析结果获取删除的记录数
        # 结果格式类似于 "DELETE 10"
        parts = result.split()
        if len(parts) >= 2:
            return int(parts[1])
        return 0
    
    async def get_top_inflow_stocks(self, trade_date: str, limit: int = 10) -> List[MoneyflowData]:
        """
        Get stocks with top capital inflow for a specific date.
        
        Args:
            trade_date (str): The trade date in 'YYYYMMDD' format
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[MoneyflowData]: List of moneyflow data
        """
        # 解析日期字符串为日期对象
        if isinstance(trade_date, str) and len(trade_date) == 8:
            parsed_date = datetime.date(
                int(trade_date[:4]), 
                int(trade_date[4:6]), 
                int(trade_date[6:8])
            )
        else:
            parsed_date = trade_date
            
        query = """
            SELECT * FROM moneyflow 
            WHERE trade_date = $1 
            ORDER BY net_mf_amount DESC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, parsed_date, limit)
        return [MoneyflowData(**row) for row in rows]
    
    async def get_top_outflow_stocks(self, trade_date: str, limit: int = 10) -> List[MoneyflowData]:
        """
        Get stocks with top capital outflow for a specific date.
        
        Args:
            trade_date (str): The trade date in 'YYYYMMDD' format
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[MoneyflowData]: List of moneyflow data
        """
        # 解析日期字符串为日期对象
        if isinstance(trade_date, str) and len(trade_date) == 8:
            parsed_date = datetime.date(
                int(trade_date[:4]), 
                int(trade_date[4:6]), 
                int(trade_date[6:8])
            )
        else:
            parsed_date = trade_date
            
        query = """
            SELECT * FROM moneyflow 
            WHERE trade_date = $1 
            ORDER BY net_mf_amount ASC 
            LIMIT $2
        """
        rows = await self.db.fetch(query, parsed_date, limit)
        return [MoneyflowData(**row) for row in rows]