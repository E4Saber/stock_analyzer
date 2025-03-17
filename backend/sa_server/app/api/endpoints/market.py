# app/api/endpoints/market.py
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.external.tushare_client import get_index_data
from app.external.yfinance_client import get_global_indices

router = APIRouter()

@router.get("/indices")
async def get_market_indices() -> Dict[str, Any]:
    """
    获取主要市场指数数据
    返回A股、港股、美股等主要指数的实时数据
    """
    cn_indices = []
    global_indices = []
    try:
        # 获取A股指数
        cn_indices = get_index_data()
    except Exception as e:
        print(f"获取A股指数失败: {str(e)}")
    
    try:
        # 获取全球指数
        global_indices = get_global_indices()
    except Exception as e:
        print(f"获取全球指数失败: {str(e)}")

    # 检查是否所有数据获取都失败了
    if not cn_indices and not global_indices:
        raise HTTPException(status_code=500, detail="所有市场数据获取失败")
    
    return {
        "cn_indices": cn_indices,
        "global_indices": global_indices
    }

@router.get("/heatmap")
async def get_market_heatmap() -> Dict[str, Any]:
    """
    获取市场热力图数据
    返回行业板块涨跌情况
    """
    # 这里暂时返回模拟数据，后续实现接口
    sectors = [
        {"name": "银行", "change_pct": 1.2, "avg_volume": 1000000},
        {"name": "医药", "change_pct": -0.8, "avg_volume": 890000},
        {"name": "科技", "change_pct": 2.3, "avg_volume": 1200000},
        # 更多行业...
    ]
    
    return {"sectors": sectors}