# app/api/endpoints/stock.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.external.tushare_client import get_stock_basic, get_stock_kline
from app.external.yfinance_client import get_stock_data

router = APIRouter()

@router.get("/basic/{stock_code}")
async def get_stock_basic_info(stock_code: str) -> Dict[str, Any]:
    """
    获取股票基本信息
    包括股票名称、当前价格、涨跌幅等基础信息
    """
    try:
        # 根据股票代码前缀判断是A股、港股还是美股
        if stock_code.startswith(('6', '0', '3')):  # A股
            stock_info = get_stock_basic(stock_code)
        else:  # 默认使用yfinance获取
            stock_info = get_stock_data(stock_code)
            
        return stock_info
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"获取股票信息失败: {str(e)}")

@router.get("/kline/{stock_code}")
async def get_stock_kline_data(
    stock_code: str, 
    period: str = Query("1d", description="K线周期: 1d, 5d, 1mo, 3mo, 6mo, 1y"),
    kline_type: str = Query("candlestick", description="K线类型: candlestick, line")
) -> Dict[str, Any]:
    """
    获取股票K线数据
    返回指定股票的K线数据，支持不同时间周期
    """
    try:
        # 根据股票代码前缀判断使用哪个数据源
        if stock_code.startswith(('6', '0', '3')):  # A股
            kline_data = get_stock_kline(stock_code, period)
        else:  # 默认使用yfinance获取
            kline_data = get_stock_data(stock_code, period=period)
            
        return {"code": stock_code, "period": period, "type": kline_type, "data": kline_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取K线数据失败: {str(e)}")

@router.get("/hot")
async def get_hot_stocks() -> Dict[str, Any]:
    """
    获取热门股票列表
    返回当日交易活跃或关注度高的股票
    """
    # 这里暂时返回模拟数据，后续实现接口
    hot_stocks = [
        {"code": "600519", "name": "贵州茅台", "price": 1668.00, "change_pct": 2.37},
        {"code": "000858", "name": "五粮液", "price": 168.40, "change_pct": 1.58},
        {"code": "601318", "name": "中国平安", "price": 48.25, "change_pct": -0.74},
        # 更多股票...
    ]
    
    return {"hot_stocks": hot_stocks}