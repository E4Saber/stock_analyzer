from typing import List, Optional, Dict, Any
from app.data.db_modules.stock_modules.reference_data.block_trade import BlockTradeData


class BlockTradeCRUD:
    """
    CRUD operations for block trade data.
    
    Provides methods to create, read, update, and delete block trade records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_block_trade(self, data: BlockTradeData) -> int:
        """
        Create a new block trade record in the database.
        
        Args:
            data (BlockTradeData): The block trade data to insert
            
        Returns:
            int: The ID of the created record
        """
        # 排除ID字段，这将由数据库自动处理
        data_dict = data.model_dump(exclude={'id'})
        
        # 构建列名和参数占位符
        columns = list(data_dict.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        
        query = f"""
            INSERT INTO block_trade (
                {', '.join(columns)}
            ) VALUES (
                {', '.join(placeholders)}
            ) RETURNING id
        """
        
        # 执行插入并返回新记录的ID
        return await self.db.fetchval(query, *data_dict.values())

    async def get_block_trade_by_id(self, id: int) -> Optional[BlockTradeData]:
        """
        Retrieve a block trade record by its ID.
        
        Args:
            id (int): The ID of the record to retrieve
            
        Returns:
            BlockTradeData | None: The block trade data if found, None otherwise
        """
        query = "SELECT * FROM block_trade WHERE id = $1"
        row = await self.db.fetchrow(query, id)
        return BlockTradeData.model_validate(dict(row)) if row else None
    
    async def get_block_trades_by_ts_code(self, ts_code: str, limit: int = 100) -> List[BlockTradeData]:
        """
        Retrieve block trade records for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[BlockTradeData]: The list of block trade data if found, empty list otherwise
        """
        query = """
            SELECT * FROM block_trade 
            WHERE ts_code = $1 
            ORDER BY trade_date DESC
            LIMIT $2
        """
        rows = await self.db.fetch(query, ts_code, limit)
        return [BlockTradeData.model_validate(dict(row)) for row in rows]
    
    async def get_block_trades_by_trade_date(self, trade_date: str, limit: int = 100) -> List[BlockTradeData]:
        """
        Retrieve block trade records by trade date.
        
        Args:
            trade_date (str): The trade date (YYYYMMDD format)
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[BlockTradeData]: The list of block trade data if found, empty list otherwise
        """
        # 处理trade_date格式
        formatted_trade_date = trade_date
        if trade_date and isinstance(trade_date, str):
            if trade_date.isdigit() and len(trade_date) == 8:
                formatted_trade_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:8]}"
        
        query = """
            SELECT * FROM block_trade 
            WHERE trade_date = $1::date
            ORDER BY amount DESC
            LIMIT $2
        """
        rows = await self.db.fetch(query, formatted_trade_date, limit)
        return [BlockTradeData.model_validate(dict(row)) for row in rows]
    
    async def get_block_trades_by_date_range(self, start_date: str, end_date: str, limit: int = 100) -> List[BlockTradeData]:
        """
        Retrieve block trade records within a trade date range.
        
        Args:
            start_date (str): The start date (YYYYMMDD format)
            end_date (str): The end date (YYYYMMDD format)
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[BlockTradeData]: The list of block trade data if found, empty list otherwise
        """
        # 处理日期格式
        formatted_start_date = start_date
        if start_date and isinstance(start_date, str):
            if start_date.isdigit() and len(start_date) == 8:
                formatted_start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        
        formatted_end_date = end_date
        if end_date and isinstance(end_date, str):
            if end_date.isdigit() and len(end_date) == 8:
                formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
        
        query = """
            SELECT * FROM block_trade 
            WHERE trade_date BETWEEN $1::date AND $2::date
            ORDER BY trade_date DESC, amount DESC
            LIMIT $3
        """
        rows = await self.db.fetch(query, formatted_start_date, formatted_end_date, limit)
        return [BlockTradeData.model_validate(dict(row)) for row in rows]
    
    async def get_block_trades_by_buyer(self, buyer: str, limit: int = 100) -> List[BlockTradeData]:
        """
        Retrieve block trade records by buyer.
        
        Args:
            buyer (str): The buyer name (supports partial match)
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[BlockTradeData]: The list of block trade data if found, empty list otherwise
        """
        query = """
            SELECT * FROM block_trade 
            WHERE buyer ILIKE $1
            ORDER BY trade_date DESC, amount DESC
            LIMIT $2
        """
        rows = await self.db.fetch(query, f"%{buyer}%", limit)
        return [BlockTradeData.model_validate(dict(row)) for row in rows]
    
    async def get_block_trades_by_seller(self, seller: str, limit: int = 100) -> List[BlockTradeData]:
        """
        Retrieve block trade records by seller.
        
        Args:
            seller (str): The seller name (supports partial match)
            limit (int): Maximum number of records to retrieve
            
        Returns:
            List[BlockTradeData]: The list of block trade data if found, empty list otherwise
        """
        query = """
            SELECT * FROM block_trade 
            WHERE seller ILIKE $1
            ORDER BY trade_date DESC, amount DESC
            LIMIT $2
        """
        rows = await self.db.fetch(query, f"%{seller}%", limit)
        return [BlockTradeData.model_validate(dict(row)) for row in rows]
    
    async def update_block_trade(self, id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a block trade record by its ID.
        
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
            UPDATE block_trade
            SET {set_values}
            WHERE id = $1
        """
        
        # 执行更新操作
        result = await self.db.execute(query, id, *updates.values())
        
        # 检查是否有行被更新
        return 'UPDATE 1' in result
    
    async def delete_block_trade(self, id: int) -> bool:
        """
        Delete a block trade record by its ID.
        
        Args:
            id (int): The ID of the record to delete
            
        Returns:
            bool: True if the deletion was successful, False otherwise
        """
        query = "DELETE FROM block_trade WHERE id = $1"
        result = await self.db.execute(query, id)
        
        # 检查是否有行被删除
        return 'DELETE 1' in result
    
    async def delete_block_trades_by_ts_code(self, ts_code: str) -> int:
        """
        Delete all block trade records for a specific stock.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            int: Number of records deleted
        """
        query = "DELETE FROM block_trade WHERE ts_code = $1"
        result = await self.db.execute(query, ts_code)
        
        # 提取删除的行数
        import re
        match = re.search(r'DELETE (\d+)', result)
        return int(match.group(1)) if match else 0
    
    async def delete_block_trades_by_date_range(self, start_date: str, end_date: str) -> int:
        """
        Delete block trade records within a date range.
        
        Args:
            start_date (str): The start date (YYYYMMDD format)
            end_date (str): The end date (YYYYMMDD format)
            
        Returns:
            int: Number of records deleted
        """
        # 处理日期格式
        formatted_start_date = start_date
        if start_date and isinstance(start_date, str):
            if start_date.isdigit() and len(start_date) == 8:
                formatted_start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        
        formatted_end_date = end_date
        if end_date and isinstance(end_date, str):
            if end_date.isdigit() and len(end_date) == 8:
                formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
        
        query = "DELETE FROM block_trade WHERE trade_date BETWEEN $1::date AND $2::date"
        result = await self.db.execute(query, formatted_start_date, formatted_end_date)
        
        # 提取删除的行数
        import re
        match = re.search(r'DELETE (\d+)', result)
        return int(match.group(1)) if match else 0
    
    async def get_block_trades(self, 
                            filters: Optional[Dict[str, Any]] = None, 
                            order_by: Optional[List[str]] = None,
                            limit: Optional[int] = None,
                            offset: Optional[int] = None) -> List[BlockTradeData]:
        """
        动态查询大宗交易数据，支持任意字段过滤和自定义排序
        
        参数:
            filters: 过滤条件字典，键为字段名，值为过滤值
                     支持的运算符后缀：
                     - __eq: 等于 (默认)
                     - __ne: 不等于
                     - __gt: 大于
                     - __ge: 大于等于
                     - __lt: 小于
                     - __le: 小于等于
                     - __like: LIKE模糊查询
                     - __ilike: ILIKE不区分大小写模糊查询
                     - __in: IN包含查询
                     例如: {'ts_code__like': '600%', 'trade_date__gt': '20230101'}
            order_by: 排序字段列表，可以在字段前加"-"表示降序，例如['-trade_date', 'amount']
            limit: 最大返回记录数
            offset: 跳过前面的记录数（用于分页）
            
        返回:
            List[BlockTradeData]: 符合条件的大宗交易数据列表
        """
        # 初始化查询部分
        query_parts = ["SELECT * FROM block_trade"]
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
                valid_fields = [f.name for f in BlockTradeData.model_fields.values()]
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
                elif op == 'like':
                    condition = f"{field} LIKE ${param_idx}"
                elif op == 'ilike':
                    condition = f"{field} ILIKE ${param_idx}"
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
                
                # 特殊处理日期字段，确保格式正确
                if field == 'trade_date' and value is not None:
                    # 如果是YYYYMMDD格式，转换为ISO格式
                    if isinstance(value, str) and value.isdigit() and len(value) == 8:
                        formatted_value = f"{value[:4]}-{value[4:6]}-{value[6:8]}"
                        params.append(formatted_value)
                        condition = f"{field}::date {condition.split(' ', 1)[1]}"
                    else:
                        params.append(value)
                else:
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
                valid_fields = [f.name for f in BlockTradeData.model_fields.values()]
                if actual_field not in valid_fields and actual_field != 'id':
                    raise ValueError(f"无效的排序字段: {actual_field}")
                
                order_clauses.append(f"{actual_field} {direction}")
            
            if order_clauses:
                query_parts.append("ORDER BY " + ", ".join(order_clauses))
        else:
            # 默认排序：先按交易日期降序，再按金额降序
            query_parts.append("ORDER BY trade_date DESC, amount DESC")
        
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
        
        return [BlockTradeData.model_validate(dict(row)) for row in rows]