from typing import List, Optional, Dict, Any
from app.data.db_modules.hk_stock_modules.hk_tradecal import HkTradecalData


class HkTradecalCRUD:
    """
    CRUD operations for Hong Kong trading calendar.
    
    Provides methods to create, read, update, and delete Hong Kong trading calendar records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_hk_tradecal(self, data: HkTradecalData) -> int:
        """
        Create a new Hong Kong trading calendar record in the database.
        
        Args:
            data (HkTradecalData): The calendar data to insert
            
        Returns:
            int: The ID of the created record
        """
        # 排除ID字段，这将由数据库自动处理
        data_dict = data.model_dump(exclude={'id'})
        
        # 构建列名和参数占位符
        columns = list(data_dict.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        
        query = f"""
            INSERT INTO hk_tradecal (
                {', '.join(columns)}
            ) VALUES (
                {', '.join(placeholders)}
            ) RETURNING id
        """
        
        # 执行插入并返回新记录的ID
        return await self.db.fetchval(query, *data_dict.values())

    async def get_hk_tradecal_by_id(self, id: int) -> Optional[HkTradecalData]:
        """
        Retrieve a Hong Kong trading calendar record by its ID.
        
        Args:
            id (int): The ID of the record to retrieve
            
        Returns:
            HkTradecalData | None: The calendar data if found, None otherwise
        """
        query = "SELECT * FROM hk_tradecal WHERE id = $1"
        row = await self.db.fetchrow(query, id)
        return HkTradecalData.model_validate(dict(row)) if row else None
    
    async def get_hk_tradecal_by_date(self, cal_date: str) -> Optional[HkTradecalData]:
        """
        Retrieve a Hong Kong trading calendar record by its date.
        
        Args:
            cal_date (str): The calendar date (can be in 'YYYYMMDD' or 'YYYY-MM-DD' format)
            
        Returns:
            HkTradecalData | None: The calendar data if found, None otherwise
        """
        # 处理cal_date格式，确保可以适配数据库中的日期字段
        formatted_date = cal_date
        if cal_date and isinstance(cal_date, str):
            if cal_date.isdigit() and len(cal_date) == 8:
                # 将YYYYMMDD转为YYYY-MM-DD以匹配PostgreSQL日期格式
                formatted_date = f"{cal_date[:4]}-{cal_date[4:6]}-{cal_date[6:8]}"
        
        query = "SELECT * FROM hk_tradecal WHERE cal_date = $1::date"
        row = await self.db.fetchrow(query, formatted_date)
        return HkTradecalData.model_validate(dict(row)) if row else None
    
    async def list_hk_tradecal(self, 
                             start_date: Optional[str] = None, 
                             end_date: Optional[str] = None,
                             is_open: Optional[int] = None,
                             limit: int = 100,
                             offset: int = 0) -> List[HkTradecalData]:
        """
        List Hong Kong trading calendar records with optional filtering by date range and open status.
        
        Args:
            start_date (str, optional): Start date (can be in 'YYYYMMDD' or 'YYYY-MM-DD' format)
            end_date (str, optional): End date (can be in 'YYYYMMDD' or 'YYYY-MM-DD' format)
            is_open (int, optional): Filter by trading status (0-closed, 1-open)
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[HkTradecalData]: List of Hong Kong trading calendar data
        """
        params = []
        query_parts = ["SELECT * FROM hk_tradecal"]
        
        where_clauses = []
        
        # 处理日期范围筛选
        if start_date:
            formatted_start_date = start_date
            if isinstance(start_date, str) and start_date.isdigit() and len(start_date) == 8:
                formatted_start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            where_clauses.append(f"cal_date >= ${len(params) + 1}::date")
            params.append(formatted_start_date)
        
        if end_date:
            formatted_end_date = end_date
            if isinstance(end_date, str) and end_date.isdigit() and len(end_date) == 8:
                formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
            where_clauses.append(f"cal_date <= ${len(params) + 1}::date")
            params.append(formatted_end_date)
        
        # 处理是否交易筛选
        if is_open is not None:
            where_clauses.append(f"is_open = ${len(params) + 1}")
            params.append(is_open)
        
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        query_parts.append("ORDER BY cal_date")
        query_parts.append(f"LIMIT ${len(params) + 1}")
        params.append(limit)
        
        query_parts.append(f"OFFSET ${len(params) + 1}")
        params.append(offset)
        
        query = " ".join(query_parts)
        rows = await self.db.fetch(query, *params)
        return [HkTradecalData.model_validate(dict(row)) for row in rows]
    
    async def update_hk_tradecal(self, id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a Hong Kong trading calendar record by its ID.
        
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
            UPDATE hk_tradecal
            SET {set_values}
            WHERE id = $1
        """
        
        # 执行更新操作
        result = await self.db.execute(query, id, *updates.values())
        
        # 检查是否有行被更新
        return 'UPDATE 1' in result
    
    async def update_hk_tradecal_by_date(self, cal_date: str, updates: Dict[str, Any]) -> bool:
        """
        Update a Hong Kong trading calendar record by its date.
        
        Args:
            cal_date (str): The calendar date
            updates (dict): Dictionary of fields to update and their new values
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        # 排除不应该手动更新的字段
        if 'id' in updates:
            del updates['id']
        
        # 处理cal_date格式，确保可以适配数据库中的日期字段
        formatted_date = cal_date
        if cal_date and isinstance(cal_date, str):
            if cal_date.isdigit() and len(cal_date) == 8:
                # 将YYYYMMDD转为YYYY-MM-DD以匹配PostgreSQL日期格式
                formatted_date = f"{cal_date[:4]}-{cal_date[4:6]}-{cal_date[6:8]}"
        
        # 构建SET子句
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        
        query = f"""
            UPDATE hk_tradecal
            SET {set_values}
            WHERE cal_date = $1::date
        """
        
        # 执行更新操作
        result = await self.db.execute(query, formatted_date, *updates.values())
        
        # 检查是否有行被更新
        return 'UPDATE 1' in result
    
    async def delete_hk_tradecal(self, id: int) -> bool:
        """
        Delete a Hong Kong trading calendar record by its ID.
        
        Args:
            id (int): The ID of the record to delete
            
        Returns:
            bool: True if the deletion was successful, False otherwise
        """
        query = "DELETE FROM hk_tradecal WHERE id = $1"
        result = await self.db.execute(query, id)
        
        # 检查是否有行被删除
        return 'DELETE 1' in result
    
    async def delete_hk_tradecal_by_date(self, cal_date: str) -> bool:
        """
        Delete a Hong Kong trading calendar record by its date.
        
        Args:
            cal_date (str): The calendar date
            
        Returns:
            bool: True if the deletion was successful, False otherwise
        """
        # 处理cal_date格式
        formatted_date = cal_date
        if cal_date and isinstance(cal_date, str):
            if cal_date.isdigit() and len(cal_date) == 8:
                formatted_date = f"{cal_date[:4]}-{cal_date[4:6]}-{cal_date[6:8]}"
                
        query = "DELETE FROM hk_tradecal WHERE cal_date = $1::date"
        result = await self.db.execute(query, formatted_date)
        
        # 检查是否有行被删除
        return 'DELETE 1' in result
    
    async def delete_hk_tradecal_by_date_range(self, start_date: str, end_date: str) -> int:
        """
        Delete Hong Kong trading calendar records within a date range.
        
        Args:
            start_date (str): Start date
            end_date (str): End date
            
        Returns:
            int: Number of records deleted
        """
        # 处理日期格式
        formatted_start_date = start_date
        if start_date and isinstance(start_date, str) and start_date.isdigit() and len(start_date) == 8:
            formatted_start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            
        formatted_end_date = end_date
        if end_date and isinstance(end_date, str) and end_date.isdigit() and len(end_date) == 8:
            formatted_end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
                
        query = "DELETE FROM hk_tradecal WHERE cal_date BETWEEN $1::date AND $2::date"
        result = await self.db.execute(query, formatted_start_date, formatted_end_date)
        
        # 提取删除的行数
        import re
        match = re.search(r'DELETE (\d+)', result)
        return int(match.group(1)) if match else 0
    
    async def get_hk_tradecal(self, 
                            filters: Optional[Dict[str, Any]] = None, 
                            order_by: Optional[List[str]] = None,
                            limit: Optional[int] = None,
                            offset: Optional[int] = None) -> List[HkTradecalData]:
        """
        动态查询香港交易日历数据，支持任意字段过滤和自定义排序
        
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
                     例如: {'is_open': 1, 'cal_date__gt': '20230101'}
            order_by: 排序字段列表，可以在字段前加"-"表示降序，例如['-cal_date']
            limit: 最大返回记录数
            offset: 跳过前面的记录数（用于分页）
            
        返回:
            List[HkTradecalData]: 符合条件的香港交易日历数据列表
        """
        # 初始化查询部分
        query_parts = ["SELECT * FROM hk_tradecal"]
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
                valid_fields = [f.name for f in HkTradecalData.model_fields.values()]
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
                
                # 特殊处理日期字段，确保格式正确
                if field in ['cal_date', 'pretrade_date'] and value is not None:
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
                valid_fields = [f.name for f in HkTradecalData.model_fields.values()]
                if actual_field not in valid_fields and actual_field != 'id':
                    raise ValueError(f"无效的排序字段: {actual_field}")
                
                order_clauses.append(f"{actual_field} {direction}")
            
            if order_clauses:
                query_parts.append("ORDER BY " + ", ".join(order_clauses))
        else:
            # 默认排序：按日期
            query_parts.append("ORDER BY cal_date")
        
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
        
        return [HkTradecalData.model_validate(dict(row)) for row in rows]