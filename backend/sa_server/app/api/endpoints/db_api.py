# app/api/endpoints/db_api.py
from fastapi import APIRouter
from app.db.db import get_db
from databases import Database
from typing import Optional
from pydantic import BaseModel
from fastapi import Depends
from app.services.db_services.stock_basic_service import import_single_stock
from fastapi import HTTPException
from app.db.crud.stock_basic_crud import StockBasicCRUD


router = APIRouter()

class ImportResponse(BaseModel):
    """导入响应模型"""
    success: bool
    message: str
    count: Optional[int] = None

@router.get("/test")
async def test_route():
    return {"message": "Test route works!"}

@router.get("/get_stock_basic/{ts_code}")
async def get_db_api(ts_code: str) -> str:
    """
    获取数据库操作API
    """
    db = await get_db()
    stockBasicCRUD = StockBasicCRUD(db)
    stockBasicData = await stockBasicCRUD.get_stock_by_ts_code(ts_code)

    if not stockBasicData:
        raise HTTPException(status_code=404, detail=f"股票代码 {ts_code} 未找到")


    return stockBasicData

@router.post("/import/{ts_code}", response_model=ImportResponse)
async def import_stock_data(ts_code: str, db: Database = Depends(get_db)):
    """
    导入单个股票基础数据
    
    参数:
        ts_code: 股票TS代码，例如 "000001.SZ"
    """
    try:
        success = await import_single_stock(db, ts_code)
        if success:
            return {
                "success": True,
                "message": f"成功导入股票 {ts_code}",
                "count": 1
            }
        else:
            return {
                "success": False,
                "message": f"未找到股票 {ts_code} 或导入失败",
                "count": 0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入股票数据失败: {str(e)}")
