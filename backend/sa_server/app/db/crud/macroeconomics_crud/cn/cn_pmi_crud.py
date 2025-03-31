from typing import List, Optional, Dict, Any
from app.data.db_modules.macroeconomics_modules.cn.cn_pmi import CnPmiData


class CnPmiCRUD:
    """
    CRUD operations for China PMI data.
    
    Provides methods to create, read, update, and delete PMI records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_pmi(self, data: CnPmiData) -> None:
        """
        Create a new PMI record in the database.
        
        Args:
            data (CnPmiData): The PMI data to insert
        """
        # 获取所有非None字段构建动态插入语句
        fields = []
        values = []
        placeholders = []
        idx = 1
        
        for key, value in data.model_dump().items():
            if value is not None:
                fields.append(key)
                values.append(value)
                placeholders.append(f"${idx}")
                idx += 1
        
        fields_str = ', '.join(fields)
        placeholders_str = ', '.join(placeholders)
        
        query = f"""
            INSERT INTO cn_pmi ({fields_str})
            VALUES ({placeholders_str})
        """
        
        await self.db.execute(query, *values)

    async def get_pmi_by_month(self, month: str) -> Optional[CnPmiData]:
        """
        Retrieve a PMI record by month.
        
        Args:
            month (str): The month in YYYYMM format
            
        Returns:
            CnPmiData | None: The PMI data if found, None otherwise
        """
        query = "SELECT * FROM cn_pmi WHERE month = $1"
        row = await self.db.fetchrow(query, month)
        return CnPmiData(**row) if row else None
    
    async def get_pmi_range(self, start_month: str, end_month: str) -> List[CnPmiData]:
        """
        Retrieve PMI records within a month range.
        
        Args:
            start_month (str): Starting month in YYYYMM format
            end_month (str): Ending month in YYYYMM format
            
        Returns:
            List[CnPmiData]: List of PMI data within the range
        """
        query = "SELECT * FROM cn_pmi WHERE month >= $1 AND month <= $2 ORDER BY month"
        rows = await self.db.fetch(query, start_month, end_month)
        return [CnPmiData(**row) for row in rows]
    
    async def update_pmi(self, month: str, updates: dict) -> None:
        """
        Update a PMI record by month.
        
        Args:
            month (str): The month in YYYYMM format to update
            updates (dict): Dictionary of fields to update and their new values
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE cn_pmi
            SET {set_values}
            WHERE month = $1
        """
        await self.db.execute(query, month, *updates.values())
    
    async def delete_pmi(self, month: str) -> None:
        """
        Delete a PMI record by month.
        
        Args:
            month (str): The month in YYYYMM format of the PMI data to delete
        """
        query = "DELETE FROM cn_pmi WHERE month = $1"
        await self.db.execute(query, month)
    
    async def list_pmi(self, limit: int = 60, offset: int = 0) -> List[CnPmiData]:
        """
        List PMI records with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve, default is 60 (5 years)
            offset (int): Number of records to skip
            
        Returns:
            List[CnPmiData]: List of PMI data
        """
        query = "SELECT * FROM cn_pmi ORDER BY month DESC LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [CnPmiData(**row) for row in rows]
    
    async def get_latest_pmi(self) -> Optional[CnPmiData]:
        """
        Retrieve the latest PMI record.
        
        Returns:
            CnPmiData | None: The latest PMI data if available, None otherwise
        """
        query = "SELECT * FROM cn_pmi ORDER BY month DESC LIMIT 1"
        row = await self.db.fetchrow(query)
        return CnPmiData(**row) if row else None
    
    async def get_yearly_pmi(self, year: str) -> List[CnPmiData]:
        """
        Retrieve PMI records for a specific year.
        
        Args:
            year (str): Year in YYYY format
            
        Returns:
            List[CnPmiData]: List of PMI data for the specified year
        """
        start_month = f"{year}01"
        end_month = f"{year}12"
        query = "SELECT * FROM cn_pmi WHERE month >= $1 AND month <= $2 ORDER BY month"
        rows = await self.db.fetch(query, start_month, end_month)
        return [CnPmiData(**row) for row in rows]
    
    async def get_pmi_with_fields(self, months: List[str], fields: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve specific PMI fields for given months.
        
        Args:
            months (List[str]): List of months in YYYYMM format
            fields (List[str]): List of PMI fields to retrieve
            
        Returns:
            List[dict]: List of dictionaries with the specified fields
        """
        fields_str = ', '.join(['month'] + fields)
        placeholders = ', '.join([f'${i+1}' for i in range(len(months))])
        
        query = f"SELECT {fields_str} FROM cn_pmi WHERE month IN ({placeholders}) ORDER BY month"
        rows = await self.db.fetch(query, *months)
        return [dict(row) for row in rows]
        
    async def get_monthly_comparison(self, month1: str, month2: str) -> Dict[str, Any]:
        """
        比较两个月份的PMI数据
        
        Args:
            month1 (str): 第一个月份，YYYYMM格式
            month2 (str): 第二个月份，YYYYMM格式
            
        Returns:
            Dict[str, Any]: 两个月份的PMI数据对比
        """
        query = """
            SELECT * FROM cn_pmi 
            WHERE month IN ($1, $2)
        """
        rows = await self.db.fetch(query, month1, month2)
        
        if len(rows) < 2:
            return {"error": "未找到对比月份的数据"}
            
        # 创建结果字典
        result = {
            "months": [month1, month2],
            "data": {}
        }
        
        # 转换为字典进行比较
        data = {}
        for row in rows:
            row_dict = dict(row)
            month = row_dict.pop("month")
            data[month] = row_dict
            
        # 计算每个字段的差异
        for field in data[month1].keys():
            # 跳过非数值字段
            if not isinstance(data[month1][field], (int, float)) or data[month1][field] is None or data[month2][field] is None:
                continue
                
            result["data"][field] = {
                "values": [float(data[month1][field]), float(data[month2][field])],
                "change": float(data[month2][field]) - float(data[month1][field])
            }
            
        return result
    
    async def get_pmi_aggregate(self, start_month: str, end_month: str) -> Dict[str, Any]:
        """
        获取PMI数据的汇总统计
        
        Args:
            start_month (str): 开始月份，YYYYMM格式
            end_month (str): 结束月份，YYYYMM格式
            
        Returns:
            Dict[str, Any]: PMI数据统计结果
        """
        query = """
            SELECT * FROM cn_pmi 
            WHERE month >= $1 AND month <= $2
            ORDER BY month
        """
        rows = await self.db.fetch(query, start_month, end_month)
        
        if not rows:
            return {"error": "未找到指定时间段的数据"}
            
        # 转换为字典列表
        data_list = [dict(row) for row in rows]
        
        # 计算统计指标
        result = {
            "period": {
                "start_month": start_month,
                "end_month": end_month,
                "months_count": len(data_list)
            },
            "stats": {}
        }
        
        # 数值字段的汇总统计
        for field in data_list[0].keys():
            if field == "month":
                continue
                
            values = [row[field] for row in data_list if row[field] is not None]
            if not values or not all(isinstance(v, (int, float)) for v in values):
                continue
                
            # 统计项
            stats = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "range": max(values) - min(values),
                "latest": values[-1],
                "count": len(values)
            }
            
            # 计算标准差
            if len(values) > 1:
                mean = stats["mean"]
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                stats["std"] = variance ** 0.5
            
            result["stats"][field] = stats
            
        return result
    
    async def get_pmi_trend_indicators(self, field: str, periods: int = 12) -> Dict[str, Any]:
        """
        计算PMI指标的趋势指标
        
        Args:
            field (str): PMI字段名称
            periods (int): 分析的期数，默认12个月
            
        Returns:
            Dict[str, Any]: 趋势指标数据
        """
        query = f"""
            SELECT month, {field} FROM cn_pmi 
            ORDER BY month DESC
            LIMIT $1
        """
        rows = await self.db.fetch(query, periods)
        
        if not rows:
            return {"error": f"未找到{field}字段的数据"}
            
        # 转换为字典列表并反转顺序（从旧到新）
        data_list = [dict(row) for row in rows]
        data_list.reverse()
        
        months = [row["month"] for row in data_list]
        values = [float(row[field]) if row[field] is not None else None for row in data_list]
        
        # 过滤掉None值
        valid_values = [v for v in values if v is not None]
        
        if not valid_values:
            return {"error": f"{field}字段没有有效数据"}
            
        # 计算基本趋势指标
        result = {
            "field": field,
            "periods": len(valid_values),
            "months": months,
            "values": values,
            "min": min(valid_values),
            "max": max(valid_values),
            "mean": sum(valid_values) / len(valid_values),
            "latest": valid_values[-1]
        }
        
        # 计算环比变化
        if len(valid_values) >= 2:
            mom_changes = [valid_values[i] - valid_values[i-1] for i in range(1, len(valid_values))]
            result["monthly_changes"] = mom_changes
            result["trend"] = "上升" if mom_changes[-1] > 0 else "下降"
        
        # 计算连续上升/下降月份数
        consecutive_count = 1
        for i in range(len(valid_values)-1, 0, -1):
            if (valid_values[i] > valid_values[i-1] and valid_values[i-1] > valid_values[i-2]) or \
               (valid_values[i] < valid_values[i-1] and valid_values[i-1] < valid_values[i-2]):
                consecutive_count += 1
            else:
                break
                
        result["consecutive_count"] = consecutive_count
        
        # 计算超过/低于荣枯线的月份数
        above_50 = sum(1 for v in valid_values if v >= 50)
        below_50 = sum(1 for v in valid_values if v < 50)
        result["above_50_count"] = above_50
        result["below_50_count"] = below_50
        result["primary_state"] = "扩张" if above_50 > below_50 else "收缩"
        
        return result
    
    async def bulk_delete_pmi(self, months: List[str]) -> int:
        """
        批量删除PMI记录
        
        Args:
            months (List[str]): 要删除的月份列表，YYYYMM格式
            
        Returns:
            int: 删除的记录数
        """
        if not months:
            return 0
            
        placeholders = ', '.join([f'${i+1}' for i in range(len(months))])
        query = f"DELETE FROM cn_pmi WHERE month IN ({placeholders})"
        
        result = await self.db.execute(query, *months)
        # 解析结果获取删除的记录数
        # 结果格式类似于 "DELETE 10"
        parts = result.split()
        if len(parts) >= 2:
            return int(parts[1])
        return 0