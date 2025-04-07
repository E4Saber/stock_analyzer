from typing import List, Optional, Dict, Any
from app.data.db_modules.hk_stock_modules.hk_basic import HkBasicData


class HkBasicCRUD:
    """
    CRUD operations for Hong Kong stock basic information.
    
    Provides methods to create, read, update, and delete Hong Kong stock basic records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_hk_basic(self, data: HkBasicData) -> int:
        """
        Create a new Hong Kong stock basic record in the database.
        
        Args:
            data (HkBasicData): The stock data to insert
            
        Returns:
            int: The ID of the created record
        """
        # 排除ID字段，这将由数据库自动处理
        data_dict = data.model_dump(exclude={'id'})
        
        # 构建列名和参数占位符
        columns = list(data_dict.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        
        query = f"""
            INSERT INTO hk_basic (
                {', '.join(columns)}
            ) VALUES (
                {', '.join(placeholders)}
            ) RETURNING id
        """
        
        # 执行插入并返回新记录的ID
        return await self.db.fetchval(query, *data_dict.values())

    async def get_hk_basic_by_id(self, id: int) -> Optional[HkBasicData]:
        """
        Retrieve a Hong Kong stock basic record by its ID.
        
        Args:
            id (int): The ID of the record to retrieve
            
        Returns:
            HkBasicData | None: The stock data if found, None otherwise
        """
        query = "SELECT * FROM hk_basic WHERE id = $1"
        row = await self.db.fetchrow(query, id)
        return HkBasicData.model_validate(dict(row)) if row else None
    
    async def get_hk_basic_by_ts_code(self, ts_code: str) -> Optional[HkBasicData]:
        """
        Retrieve a Hong Kong stock basic record by its TS code.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            HkBasicData | None: The stock data if found, None otherwise
        """
        query = "SELECT * FROM hk_basic WHERE ts_code = $1"
        row = await self.db.fetchrow(query, ts_code)
        return HkBasicData.model_validate(dict(row)) if row else None
    
    async def list_hk_basic(self, 
                           list_status: Optional[str] = None,
                           limit: int = 100, 
                           offset: int = 0) -> List[HkBasicData]:
        """
        List Hong Kong stock basic records with optional filtering by list status.
        
        Args:
            list_status (str, optional): Filter by listing status (L, D, P)
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[HkBasicData]: List of Hong Kong stock basic data
        """
        params = []
        query_parts = ["SELECT * FROM hk_basic"]
        
        where_clauses = []
        if list_status:
            where_clauses.append("list_status = $1")
            params.append(list_status)
        
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        query_parts.append("ORDER BY ts_code")
        query_parts.append(f"LIMIT ${len(params) + 1}")
        params.append(limit)
        
        query_parts.append(f"OFFSET ${len(params) + 1}")
        params.append(offset)
        
        query = " ".join(query_parts)
        rows = await self.db.fetch(query, *params)
        return [HkBasicData.model_validate(dict(row)) for row in rows]
    
    async def update_hk_basic(self, id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a Hong Kong stock basic record by its ID.
        
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
            UPDATE hk_basic
            SET {set_values}
            WHERE id = $1
        """
        
        # 执行更新操作
        result = await self.db.execute(query, id, *updates.values())
        
        # 检查是否有行被更新
        return 'UPDATE 1' in result
    
    async def update_hk_basic_by_ts_code(self, ts_code: str, updates: Dict[str, Any]) -> bool:
        """
        Update a Hong Kong stock basic record by its TS code.
        
        Args:
            ts_code (str): The TS code of the stock
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
            UPDATE hk_basic
            SET {set_values}
            WHERE ts_code = $1
        """
        
        # 执行更新操作
        result = await self.db.execute(query, ts_code, *updates.values())
        
        # 检查是否有行被更新
        return 'UPDATE 1' in result
    
    async def delete_hk_basic(self, id: int) -> bool:
        """
        Delete a Hong Kong stock basic record by its ID.
        
        Args:
            id (int): The ID of the record to delete
            
        Returns:
            bool: True if the deletion was successful, False otherwise
        """
        query = "DELETE FROM hk_basic WHERE id = $1"
        result = await self.db.execute(query, id)
        
        # 检查是否有行被删除
        return 'DELETE 1' in result
    
    async def delete_hk_basic_by_ts_code(self, ts_code: str) -> bool:
        """
        Delete a Hong Kong stock basic record by its TS code.
        
        Args:
            ts_code (str): The TS code of the stock
            
        Returns:
            bool: True if the deletion was successful, False otherwise
        """
        query = "DELETE FROM hk_basic WHERE ts_code = $1"
        result = await self.db.execute(query, ts_code)
        
        # 检查是否有行被删除
        return 'DELETE 1' in result
    
    async def get_hk_basic(self, 
                          filters: Optional[Dict[str, Any]] = None, 
                          order_by: Optional[List[str]] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None) -> List[HkBasicData]:
        """
        动态查询香港股票基本信息，支持任意字段过滤和自定义排序
        
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
                     例如: {'list_status': 'L', 'name__ilike': '%银行%'}
            order_by: 排序字段列表，可以在字段前加"-"表示降序，例如['-list_date', 'name']
            limit: 最大返回记录数
            offset: 跳过前面的记录数（用于分页）
            
        返回:
            List[HkBasicData]: 符合条件的香港股票基本信息列表
        """
        # 初始化查询部分
        query_parts = ["SELECT * FROM hk_basic"]
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
                valid_fields = [f.name for f in HkBasicData.model_fields.values()]
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
                if field in ['list_date', 'delist_date'] and value is not None:
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
                valid_fields = [f.name for f in HkBasicData.model_fields.values()]
                if actual_field not in valid_fields and actual_field != 'id':
                    raise ValueError(f"无效的排序字段: {actual_field}")
                
                order_clauses.append(f"{actual_field} {direction}")
            
            if order_clauses:
                query_parts.append("ORDER BY " + ", ".join(order_clauses))
        else:
            # 默认排序：按TS代码
            query_parts.append("ORDER BY ts_code")
        
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
        
        return [HkBasicData.model_validate(dict(row)) for row in rows]