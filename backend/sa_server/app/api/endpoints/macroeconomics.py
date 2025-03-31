from fastapi import APIRouter
from typing import List, Optional
from fastapi import HTTPException
from fastapi import Query
from app.data.db_modules.macroeconomics_modules.cn.cn_gdp import CnGdpData
from app.db.crud.macroeconomics_crud.cn.cn_gdp_crud import CnGdpCRUD
from app.data.db_modules.macroeconomics_modules.cn.cn_cpi import CnCpiData
from app.db.crud.macroeconomics_crud.cn.cn_cpi_crud import CnCpiCRUD
from app.db.db import get_db

router = APIRouter()


@router.get("/cn_cpi", response_model=List[CnCpiData])
async def get_macroeconomics_cn_cpi(
    year: Optional[int] = None,
    months: Optional[int] = None,
    start_month: Optional[str] = None,
    end_month: Optional[str] = None
):
    """
    获取中国CPI数据。
    
    可以通过以下几种方式筛选数据：
    - 指定年份(year)：获取特定年份的所有CPI数据
    - 指定月数(months)：获取最近几个月的CPI数据
    - 指定起止月份(start_month, end_month)：获取指定月份范围内的CPI数据
    - 不指定参数：获取所有CPI数据
    
    Args:
        year: 年份，例如: 2023
        months: 最近几个月，例如: 12
        start_month: 起始月份，格式: YYYYMM，例如: 202301
        end_month: 结束月份，格式: YYYYMM，例如: 202312
    
    Returns:
        List[CnCpiData]: CPI数据列表
    """
    print(f"获取CPI数据: year={year}, months={months}, start_month={start_month}, end_month={end_month}")
    try:
        db = await get_db()
        cn_cpi_crud = CnCpiCRUD(db)
        
        # 根据不同的参数选择不同的查询方式
        if year is not None:
            # 获取特定年份的数据
            result = await cn_cpi_crud.get_year_cpi(year)
        elif months is not None:
            # 获取最近几个月的数据
            result = await cn_cpi_crud.get_cpi_trend(months)
        elif start_month is not None and end_month is not None:
            # 获取特定月份范围的数据
            result = await cn_cpi_crud.get_cpi_range(start_month, end_month)
        else:
            # 获取所有数据
            result = await cn_cpi_crud.get_all_cpi()
        
        if not result:
            return []
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取CPI数据失败: {str(e)}")


@router.get("/cn_cpi/latest")
async def get_latest_cn_cpi():
    """
    获取最新的CPI数据。
    
    Returns:
        CnCpiData: 最新的CPI数据
    """
    try:
        db = await get_db()
        cn_cpi_crud = CnCpiCRUD(db)
        
        result = await cn_cpi_crud.get_latest_cpi()
        
        if not result:
            raise HTTPException(status_code=404, detail="未找到CPI数据")
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最新CPI数据失败: {str(e)}")


@router.get("/cn_cpi/trend")
async def get_cn_cpi_trend(months: int = Query(12, ge=1, le=60)):
    """
    获取CPI趋势数据，用于图表展示。
    
    Args:
        months: 要获取的月数，默认12个月，范围1-60
    
    Returns:
        List[dict]: CPI趋势数据，包含月份、值和增长率
    """
    try:
        db = await get_db()
        cn_cpi_crud = CnCpiCRUD(db)
        
        result = await cn_cpi_crud.get_cpi_trend(months)
        
        if not result:
            return []
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取CPI趋势数据失败: {str(e)}")


if __name__ == "__main__":
    import asyncio
    result = asyncio.run(get_macroeconomics_cn_cpi())
    print(f'CPI数据: {result}')