# app/api/endpoints/market.py
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.external.tushare_client import get_cn_indices
from app.external.yfinance_client import get_global_indices
from app.services.tushare_services import get_minimal_cn_indices_tday
from app.services.yfinance_services import get_minimal_global_indices_tday
from app.utils.ui_data_transformer import get_minial_market_indices
from app.utils.data_formater import get_minimal_global_indices
from app.config.indices_config import GLOBAL_INDICES, CN_INDICES

router = APIRouter()

@router.get("/indices")
async def get_market_indices() -> Dict[str, Any]:
    """
    获取主要市场指数数据（详细，用来绘制日/周/月/年蜡烛图）
    返回A股、港股、美股等主要指数的数据，非实时
    """
    cn_indices = []
    global_indices = []
    try:
        # 获取A股指数
        cn_indices = get_cn_indices()
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

@router.get("/minimal_indices")
async def get_minimal_market_indices() -> Dict[str, Any]:
    """
    获取主要市场指数数据（精简版）
    返回A股、港股、美股等主要指数的数据，非实时
    """
    # cn_indices = []
    # global_indices = []
    try:
        # 获取A股指数
        cn_market_indeices = get_minimal_cn_indices_tday(CN_INDICES)
    except Exception as e:
        print(f"获取A股指数失败: {str(e)}")
    
    try:
        # 获取全球指数
        global_indices = get_minimal_global_indices_tday(GLOBAL_INDICES)
        global_market_indeices = get_minimal_global_indices(global_indices)
    except Exception as e:
        print(f"获取全球指数失败: {str(e)}")

    # 检查是否所有数据获取都失败了
    if not cn_market_indeices and not global_market_indeices:
        raise HTTPException(status_code=500, detail="所有市场数据获取失败")
    
    return get_minial_market_indices(cn_market_indeices, global_market_indeices)

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

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(get_minimal_market_indices())
    print(result)