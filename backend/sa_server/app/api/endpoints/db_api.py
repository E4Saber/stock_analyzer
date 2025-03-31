# app/api/endpoints/db_api.py
from app.db.db import get_db
from fastapi import APIRouter
from fastapi import Query, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.response.error_code import ErrorCode
from app.response.response_model import ResponseModel, handle_exception
from app.response.handle_exception import api_exception_handler

from app.services.db_services.stock_service.stock_financial.express_service import query_express_data


stock_router_prefix= "/stocks"
stock_basic_router_prefix = "/stock_basic"
fund_flows_router_prefix = "/fund_flows"
stock_financial_router_prefix = "/stock_financial"


stock_basic_router = APIRouter(prefix=stock_router_prefix, tags=["股票基本信息"])




# 查询参数文档（用于文档和验证）
class ExpressQueryParams(BaseModel):
    """业绩快报查询参数模型"""
    # 过滤字段
    ts_code: Optional[str] = Field(None, description="股票代码")
    ts_code__like: Optional[str] = Field(None, description="股票代码，模糊查询匹配如'000001%'")
    ann_date: Optional[str] = Field(None, description="公告日期，格式YYYYMMDD")
    ann_date__gt: Optional[str] = Field(None, description="公告日期大于指定值，格式YYYYMMDD")
    ann_date__lt: Optional[str] = Field(None, description="公告日期小于指定值，格式YYYYMMDD")

    # 排序和分页
    order_by: Optional[List[str]] = Field(
        None,
        description="排序字段，支持多个字段排序，前缀'-'表示降序，如['-ann_date', 'ts_code']",
    )
    limit: Optional[int] = Field(20, ge=1, le=20, description="返回记录数限制")
    offset: Optional[int] = Field(0, ge=0, description="分页偏移量")


# 前端调用示例（JavaScript/Axios）
"""
// 示例1: 查询2022年以来营业收入同比增长超50%的公司
axios.get('/express/query', {
    params: {
        end_date__gt: '20220101',
        yoy_sales__gt: 50,
        order_by: ['-yoy_sales'],
        limit: 20
    }
})

// 示例2: 查询特定股票的业绩快报
axios.get('/express/query', {
    params: {
        ts_code: '600000.SH',
        order_by: ['-end_date'],
        limit: 10
    }
})

// 示例3: 查询最近业绩增长最快的公司
axios.get('/express/query', {
    params: {
        yoy_dedu_np__gt: 50,
        order_by: ['-yoy_dedu_np'],
        limit: 20
    }
})
"""
@api_exception_handler
@stock_basic_router.get(stock_financial_router_prefix + "/get_express_data", response_model=ResponseModel)
async def get_express_data(
    # Query参数映射
    ts_code: Optional[str] = Query(None, description="股票代码"),
    ts_code__like: Optional[str] = Query(None, description="股票代码，模糊查询匹配如'000001%'"),
    ann_date: Optional[str] = Query(None, description="公告日期，格式YYYYMMDD"),
    ann_date__gt: Optional[str] = Query(None, description="公告日期大于指定值，格式YYYYMMDD"),
    ann_date__lt: Optional[str] = Query(None, description="公告日期小于指定值，格式YYYYMMDD"),
    order_by: Optional[List[str]] = Query(None, description="排序字段，支持多个字段排序，前缀'-'表示降序，如['-ann_date', 'ts_code']"),
    limit: int = Query(20, ge=1, le=20, description="返回记录数限制"),
    offset: int = Query(0, ge=0, description="分页偏移量"),
    db = Depends(get_db)
):
    """
        灵活查询业绩快报数据
        
        查询参数支持多种操作:
        - 精确匹配: ts_code=600000.SH
        - 模糊匹配: ts_code__like=600%
        - 比较操作: ann_date__gt=20220101
        - 排序: order_by=-ann_date,ts_code
        - 分页: limit=20, offset=0
    """
    try:
        # 构建过滤条件
        filters: Dict[str, Any] = {}
        
        # 添加各种过滤条件
        if ts_code:
            filters['ts_code'] = ts_code
        if ts_code__like:
            filters['ts_code__like'] = ts_code__like
        if ann_date:
            filters['ann_date'] = ann_date
        if ann_date__gt:
            filters['ann_date__gt'] = ann_date__gt
        if ann_date__lt:
            filters['ann_date__lt'] = ann_date__lt
        

        express_data = await query_express_data(db, 
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset
        )

        if not express_data:
            return ResponseModel.error(ErrorCode.DATA_NOT_EXISTS, "未找到快报数据")
        
        return ResponseModel.success(data=express_data)
    except Exception as e:
        return handle_exception(e, ErrorCode.DATABASE_ERROR)




