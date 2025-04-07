from typing import List, Optional, Dict, Any
from app.data.db_modules.hk_stock_modules.hk_mins import HkMinsData


class HkMinsCRUD:
    """
    CRUD operations for Hong Kong stock minute-level market data.
    
    Provides methods to create, read, update, and delete Hong Kong stock minute-level records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_hk_mins(self, data: HkMinsData) -> int:
        """
        Create a new Hong Kong stock minute-level record in the database.
        
        Args:
            data (HkMinsData): The minute-level data to insert
            
        Returns:
            int: The ID of the created record
        """
        # 排除ID字段，这将由数据库自动处理
        data_dict = data.model_dump(exclude={'id'})
        
        # 构建列名和参数占位符
        columns = list(data_dict.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        
        query = f"""
            INSERT INTO hk_mins (
                {', '.join(columns)}
            ) VALUES (
                {', '.join(placeholders)}
            ) RETURNING id
        """
        
        # 执行插入并返回新记录的ID
        return await self.db.fetchval(query, *data_dict.values())

    async def get_hk_mins_by_id(self, id: int) -> Optional[HkMinsData]:
        """
        Retrieve a Hong Kong stock minute-level record by its ID.
        
        Args:
            id (int): The ID of the record to retrieve
            
        Returns:
            HkMinsData | None: The minute-level data if found, None otherwise
        """
        query = "SELECT * FROM hk_mins WHERE id = $1"
        row = await self.db.fetchrow(query, id)
        return HkMinsData.model_validate(dict(row)) if row else None
    
    async def get_hk_mins_by_key(self, ts_code: str, trade_time: str, freq: str) -> Optional[HkMinsData]:
        """
        Retrieve a Hong Kong stock minute-level record by its unique key (ts_code, trade_time, and freq).
        
        Args:
            ts_code (str): The stock code
            trade_time (str): The trade time (can be in 'YYYY-MM-DD HH:MM:SS' format)
            freq (str): The frequency (1min/5min/15min/30min/60min)
            
        Returns:
            HkMinsData | None: The minute-level data if found, None otherwise
        """
        query = "SELECT * FROM hk_mins WHERE ts_code = $1 AND trade_time = $2::timestamp AND freq = $3"
        row = await self.db.fetchrow(query, ts_code, trade_time, freq)
        return HkMinsData.model_validate(dict(row)) if row else None
    
    async def list_hk_mins_by_ts_code_and_freq(self, 
                                             ts_code: str, 
                                             freq: str,
                                             start_time: Optional[str] = None, 
                                             end_time: Optional[str] = None,
                                             limit: int = 1000,
                                             offset: int = 0) -> List[HkMinsData]:
        """
        List Hong Kong stock minute-level records for a specific stock code and frequency with optional time range.
        
        Args:
            ts_code (str): The stock code
            freq (str): The frequency (1min/5min/15min/30min/60min)
            start_time (str, optional): Start time (can be in 'YYYY-MM-DD HH:MM:SS' format)
            end_time (str, optional): End time (can be in 'YYYY-MM-DD HH:MM:SS' format)
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[HkMinsData]: List of Hong Kong stock minute-level data
        """
        params = [ts_code, freq]
        query_parts = ["SELECT * FROM hk_mins WHERE ts_code = $1 AND freq = $2"]
        
        # 处理时间范围筛选
        if start_time:
            query_parts.append(f"AND trade_time >= ${len(params) + 1}::timestamp")
            params.append(start_time)
        
        if end_time:
            query_parts.append(f"AND trade_time <= ${len(params) + 1}::timestamp")
            params.append(end_time)
        
        query_parts.append("ORDER BY trade_time")
        query_parts.append(f"LIMIT ${len(params) + 1}")
        params.append(limit)
        
        query_parts.append(f"OFFSET ${len(params) + 1}")
        params.append(offset)
        
        query = " ".join(query_parts)
        rows = await self.db.fetch(query, *params)
        return [HkMinsData.model_validate(dict(row)) for row in rows]
    
    async def list_hk_mins_by_date_and_freq(self, 
                                          date: str,
                                          freq: str,
                                          limit: int = 1000,
                                          offset: int = 0) -> List[HkMinsData]:
        """
        List Hong Kong stock minute-level records for a specific date and frequency.
        
        Args:
            date (str): The date (can be in 'YYYY-MM-DD' format)
            freq (str): The frequency (1min/5min/15min/30min/60min)
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[HkMinsData]: List of Hong Kong stock minute-level data
        """
        query = """
            SELECT * FROM hk_mins 
            WHERE DATE(trade_time) = $1::date AND freq = $2
            ORDER BY ts_code, trade_time
            LIMIT $3 OFFSET $4
        """
        rows = await self.db.fetch(query, date, freq, limit, offset)
        return [HkMinsData.model_validate(dict(row)) for row in rows]
    
    async def update_hk_mins(self, id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a Hong Kong stock minute-level record by its ID.
        
        Args:
            id (int): The ID of the record to update
            updates (dict): Dictionary of fields to update and their new values
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        # 排除不应该手动更新的字段
        if 'id' in updates:
            del updates['id']
        
        # 构建SET子句
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        
        query = f"""
            UPDATE hk_mins
            SET {set_values}
            WHERE id = $1
        """
        
        # 执行更新操作
        result = await self.db.execute(query, id, *updates.values())
        
        # 检查是否有行被更新
        return 'UPDATE 1' in result
    
    async def update_hk_mins_by_key(self, ts_code: str, trade_time: str, freq: str, updates: Dict[str, Any]) -> bool:
        """
        Update a Hong Kong stock minute-level record by its unique key (ts_code, trade_time, and freq).
        
        Args:
            ts_code (str): The stock code
            trade_time (str): The trade time
            freq (str): The frequency (1min/5min/15min/30min/60min)
            updates (dict): Dictionary of fields to update and their new values
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        # 排除不应该手动更新的字段
        if 'id' in updates:
            del updates['id']
        
        # 构建SET子句
        set_values = ','.join([f"{key} = ${idx + 4}" for idx, key in enumerate(updates.keys())])
        
        query = f"""
            UPDATE hk_mins
            SET {set_values}
            WHERE ts_code = $1 AND trade_time = $2::timestamp AND freq = $3
        """
        
        # 执行更新操作
        result = await self.db.execute(query, ts_code, trade_time, freq, *updates.values())
        
        # 检查是否有行被更新
        return 'UPDATE 1' in result
    
    async def delete_hk_mins(self, id: int) -> bool:
        """
        Delete a Hong Kong stock minute-level record by its ID.
        
        Args:
            id (int): The ID of the record to delete
            
        Returns:
            bool: True if the deletion was successful, False otherwise
        """
        query = "DELETE FROM hk_mins WHERE id = $1"
        result = await self.db.execute(query, id)
        
        # 检查是否有行被删除
        return 'DELETE 1' in result
    
    async def delete_hk_mins_by_key(self, ts_code: str, trade_time: str, freq: str) -> bool:
        """
        Delete a Hong Kong stock minute-level record by its unique key (ts_code, trade_time, and freq).
        
        Args:
            ts_code (str): The stock code
            trade_time (str): The trade time
            freq (str): The frequency (1min/5min/15min/30min/60min)
            
        Returns:
            bool: True if the deletion was successful, False otherwise
        """
        query = "DELETE FROM hk_mins WHERE ts_code = $1 AND trade_time = $2::timestamp AND freq = $3"
        result = await self.db.execute(query, ts_code, trade_time, freq)
        
        # 检查是否有行被删除
        return 'DELETE 1' in result
    
    async def delete_hk_mins_by_ts_code_and_freq(self, ts_code: str, freq: str) -> int:
        """
        Delete all Hong Kong stock minute-level records for a specific stock code and frequency.
        
        Args:
            ts_code (str): The stock code
            freq (str): The frequency (1min/5min/15min/30min/60min)
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM hk_mins WHERE ts_code = $1 AND freq = $2"
        result = await self.db.execute(query, ts_code, freq)
        
        # 提取删除的行数
        import re
        match = re.search(r'DELETE (\d+)', result)
        return int(match.group(1)) if match else 0
    
    async def delete_hk_mins_by_date_and_freq(self, date: str, freq: str) -> int:
        """
        Delete all Hong Kong stock minute-level records for a specific date and frequency.
        
        Args:
            date (str): The date
            freq (str): The frequency (1min/5min/15min/30min/60min)
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM hk_mins WHERE DATE(trade_time) = $1::date AND freq = $2"
        result = await self.db.execute(query, date, freq)
        
        # 提取删除的行数
        import re
        match = re.search(r'DELETE (\d+)', result)
        return int(match.group(1)) if match else 0
    
    async def get_hk_mins(self, 
                        filters: Optional[Dict[str, Any]] = None, 
                        order_by: Optional[List[str]] = None,
                        limit: Optional[int] = None,
                        offset: Optional[int] = None) -> List[HkMinsData]:
        """
        动态查询香港股票分钟行情数据，支持任意字段过滤和自定义排序
        
        参数:
            filters: 过滤条件字典，键为字段名，值为过滤值
                     支持的运算符后缀：
                     - __eq: 等于 (默认)
                     - __ne: 不等于
                     - __gt: 大于
                     - __ge: 大于等于
                     - __lt: 小于
                     - __le: 小于等于
                     - __in: IN包含查询
                     例如: {'ts_code': '00700.HK', 'freq': '1min', 'trade_time__ge': '2023-03-13 09:00:00'}
            order_by: 排序字段列表，可以在字段前加"-"表示降序，例如['-trade_time', 'ts_code']
            limit: 最大返回记录数
            offset: 跳过前面的记录数（用于分页）
            
        返回:
            List[HkMinsData]: 符合条件的香港股票分钟行情数据列表
        """
        # 初始化查询部分
        query_parts = ["SELECT * FROM hk_mins"]
        params = []
        param_idx = 1
        
        # 处理过滤条件
        if filters and len(filters) > 0:
            where_conditions = []
            
            for key, value in filters.items():
                # 解析操作符后缀（如果有）
                if '__' in key:
                    field, op = key.split('__', 1)
                else:
                    field, op = key, 'eq'
                
                # 验证字段是否有效（避免SQL注入）
                valid_fields = [f.name for f in HkMinsData.model_fields.values()]
                if field not in valid_fields and field != 'id':
                    raise ValueError(f"无效的字段名: {field}")
                
                # 根据操作符构建条件
                if op == 'eq':
                    condition = f"{field} = ${param_idx}"
                elif op == 'ne':
                    condition = f"{field} != ${param_idx}"
                elif op == 'gt':
                    condition = f"{field} > ${param_idx}"
                elif op == 'ge':
                    condition = f"{field} >= ${param_idx}"
                elif op == 'lt':
                    condition = f"{field} < ${param_idx}"
                elif op == 'le':
                    condition = f"{field} <= ${param_idx}"
                elif op == 'in':
                    # 对于IN操作符，需要特殊处理参数
                    if not isinstance(value, (list, tuple)):
                        raise ValueError(f"IN操作符需要列表或元组类型的值: {key}={value}")
                    placeholders = [f"${param_idx + i}" for i in range(len(value))]
                    condition = f"{field} IN ({', '.join(placeholders)})"
                    params.extend(value)
                    param_idx += len(value)
                    continue  # 跳过下面的单参数添加
                else:
                    raise ValueError(f"不支持的操作符: {op}")
                
                # 特殊处理时间戳字段，确保格式正确
                if field == 'trade_time':
                    condition = f"{field} {condition.split(' ', 1)[1]}::timestamp"
                
                params.append(value)
                where_conditions.append(condition)
                param_idx += 1
            
            if where_conditions:
                query_parts.append("WHERE " + " AND ".join(where_conditions))
        
        # 处理排序
        if order_by and len(order_by) > 0:
            order_clauses = []
            
            for field in order_by:
                # 处理降序排序（字段前加"-"）
                if field.startswith('-'):
                    actual_field = field[1:]
                    direction = "DESC"
                else:
                    actual_field = field
                    direction = "ASC"
                
                # 验证字段是否有效
                valid_fields = [f.name for f in HkMinsData.model_fields.values()]
                if actual_field not in valid_fields and actual_field != 'id':
                    raise ValueError(f"无效的排序字段: {actual_field}")
                
                order_clauses.append(f"{actual_field} {direction}")
            
            if order_clauses:
                query_parts.append("ORDER BY " + ", ".join(order_clauses))
        else:
            # 默认排序：先按股票代码，再按频率，最后按交易时间
            query_parts.append("ORDER BY ts_code, freq, trade_time")
        
        # 添加LIMIT和OFFSET
        if limit is not None:
            query_parts.append(f"LIMIT ${param_idx}")
            params.append(limit)
            param_idx += 1
        
        if offset is not None:
            query_parts.append(f"OFFSET ${param_idx}")
            params.append(offset)
            param_idx += 1
        
        # 构建最终查询并执行
        query = " ".join(query_parts)
        rows = await self.db.fetch(query, *params)
        
        return [HkMinsData.model_validate(dict(row)) for row in rows]