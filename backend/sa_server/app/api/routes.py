# app/api/routes.py
from fastapi import APIRouter
from app.api.endpoints import stock, market

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(
    market.router,
    prefix="/market",
    tags=["market"],
)

api_router.include_router(
    stock.router,
    prefix="/stocks",
    tags=["stocks"],
)