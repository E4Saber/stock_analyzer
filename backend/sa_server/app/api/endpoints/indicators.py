# app/api/endpoints/macroeconomics_endpoints/indicators.py
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from app.db.db import get_db
from app.services.indicator_converter import IndicatorConverter

# 导入各指标的CRUD类
from app.db.crud.macroeconomics_crud.cn.cn_cpi_crud import CnCpiCRUD
from app.db.crud.macroeconomics_crud.cn.cn_gdp_crud import CnGdpCRUD
from app.db.crud.macroeconomics_crud.cn.cn_m_crud import CnMCRUD
from app.db.crud.macroeconomics_crud.cn.cn_pmi_crud import CnPmiCRUD

router = APIRouter()

# 支持的指标类型
SUPPORTED_INDICATORS = ['cpi', 'gdp', 'm', 'pmi']

@router.get("/indicators/data/{indicator_type}")
async def get_indicator_data(
    indicator_type: str,
    year: Optional[int] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    series: Optional[List[str]] = Query(None),
    db = Depends(get_db)
):
    """
    获取指定类型的宏观经济指标数据
    
    Args:
        indicator_type: 指标类型，如 'cpi', 'gdp', 'm', 'pmi'
        year: 可选，获取特定年份的数据
        start_period: 可选，开始期间，格式取决于指标类型 (YYYYMM 或 YYYYQQ)
        end_period: 可选，结束期间，格式取决于指标类型 (YYYYMM 或 YYYYQQ)
        limit: 可选，返回数据的最大记录数
        series: 可选，要返回的数据系列，例如对于CPI可以是 ['national', 'urban', 'rural']
        
    Returns:
        转换后的指标数据，符合前端图表组件所需格式
    """
    try:
        # 验证指标类型
        indicator_type = indicator_type.lower()
        if indicator_type not in SUPPORTED_INDICATORS:
            raise HTTPException(status_code=400, detail=f"不支持的指标类型: {indicator_type}")
        
        # 获取对应的CRUD类
        crud_classes = {
            'cpi': CnCpiCRUD,
            'gdp': CnGdpCRUD,
            'm': CnMCRUD,
            'pmi': CnPmiCRUD
        }
        
        crud_class = crud_classes.get(indicator_type)
        if not crud_class:
            raise HTTPException(status_code=500, detail=f"未找到指标类型 {indicator_type} 的CRUD类")
        
        crud = crud_class(db)
        
        # 根据参数获取数据
        data = None
        if year is not None:
            # 年度数据
            data_method = getattr(crud, f"get_year_{indicator_type}", None)
            if data_method:
                data = await data_method(year)
            else:
                # 使用通用方法，假设CRUD类中有get_by_year方法
                data = await crud.get_by_year(year)
        elif start_period and end_period:
            # 期间范围数据
            data_method = getattr(crud, f"get_{indicator_type}_range", None)
            if data_method:
                data = await data_method(start_period, end_period)
            else:
                # 使用通用方法，假设CRUD类中有get_range方法
                data = await crud.get_range(start_period, end_period)
        else:
            # 获取所有数据（有限制）
            data_method = getattr(crud, f"get_all_{indicator_type}", None)
            if data_method:
                data = await data_method()
            else:
                # 使用通用方法，假设CRUD类中有list方法
                data = await crud.list(limit=limit)
        
        if not data:
            return {}
        
        # 转换数据格式
        converted_data = IndicatorConverter.convert_by_indicator_type(indicator_type, data)
        
        # 如果指定了系列，只返回这些系列
        if series:
            filtered_data = {key: converted_data[key] for key in series if key in converted_data}
            return filtered_data
        
        return converted_data
    
    except Exception as e:
        import traceback
        print(f"获取{indicator_type}数据失败: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取{indicator_type}数据失败: {str(e)}")

@router.get("/indicators/metadata")
async def get_indicators_metadata():
    """
    获取所有支持的指标的元数据
    
    Returns:
        支持的指标列表及其描述信息
    """
    metadata = {
        "cpi": {
            "name": "消费者价格指数(CPI)",
            "description": "反映居民消费价格变化的指标",
            "frequency": "月度",
            "available_series": ["national", "urban", "rural"],
            "date_format": "YYYYMM",
            "source": "国家统计局"
        },
        "gdp": {
            "name": "国内生产总值(GDP)",
            "description": "衡量一个国家或地区经济总量的指标",
            "frequency": "季度",
            "available_series": ["gdp", "primaryIndustry", "secondaryIndustry", "tertiaryIndustry"],
            "date_format": "YYYYQQ",
            "source": "国家统计局"
        },
        "m": {
            "name": "货币供应量",
            "description": "反映一个经济体中流通中的货币总量",
            "frequency": "月度",
            "available_series": ["m0", "m1", "m2"],
            "date_format": "YYYYMM",
            "source": "中国人民银行"
        },
        "pmi": {
            "name": "采购经理人指数(PMI)",
            "description": "反映制造业和非制造业景气程度的指标",
            "frequency": "月度",
            "available_series": ["manufacturingPMI", "nonmanufacturingPMI", "compositePMI"],
            "date_format": "YYYYMM",
            "source": "国家统计局"
        }
    }
    
    return metadata